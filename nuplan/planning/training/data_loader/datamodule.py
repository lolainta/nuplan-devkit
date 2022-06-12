import logging
import random
from typing import Any, Dict, List, Optional, Tuple

import pytorch_lightning as pl
import torch
import torch.utils.data

from nuplan.planning.scenario_builder.abstract_scenario import AbstractScenario
from nuplan.planning.training.data_augmentation.abstract_data_augmentation import AbstractAugmentor
from nuplan.planning.training.data_loader.scenario_dataset import ScenarioDataset
from nuplan.planning.training.data_loader.splitter import AbstractSplitter
from nuplan.planning.training.modeling.types import FeaturesType, move_features_type_to_device
from nuplan.planning.training.preprocessing.feature_collate import FeatureCollate
from nuplan.planning.training.preprocessing.feature_preprocessor import FeaturePreprocessor

logger = logging.getLogger(__name__)

DataModuleNotSetupError = RuntimeError('Data module has not been setup, call "setup()"')


def create_dataset(
    samples: List[AbstractScenario],
    feature_preprocessor: FeaturePreprocessor,
    dataset_fraction: float,
    dataset_name: str,
    augmentors: Optional[List[AbstractAugmentor]] = None,
) -> torch.utils.data.Dataset:
    """
    Create a dataset from a list of samples.
    :param samples: List of dataset candidate samples.
    :param feature_preprocessor: Feature preprocessor object.
    :param dataset_fraction: Fraction of the dataset to load.
    :param dataset_name: Set name (train/val/test).
    :param augmentors: List of augmentor objects for providing data augmentation to data samples.
    :return: The instantiated torch dataset.
    """
    # Sample the desired fraction from the total samples
    num_keep = int(len(samples) * dataset_fraction)
    selected_scenarios = random.sample(samples, num_keep)

    logger.info(f"Number of samples in {dataset_name} set: {len(selected_scenarios)}")
    return ScenarioDataset(
        scenarios=selected_scenarios,
        feature_preprocessor=feature_preprocessor,
        augmentors=augmentors,
    )


class DataModule(pl.LightningDataModule):
    """
    Datamodule wrapping all preparation and dataset creation functionality.
    """

    def __init__(
        self,
        feature_preprocessor: FeaturePreprocessor,
        splitter: AbstractSplitter,
        all_scenarios: List[AbstractScenario],
        train_fraction: float,
        val_fraction: float,
        test_fraction: float,
        dataloader_params: Dict[str, Any],
        augmentors: Optional[List[AbstractAugmentor]] = None,
    ) -> None:
        """
        Initialize the class.
        :param feature_preprocessor: Feature preprocessor object.
        :param splitter: Splitter object used to retrieve lists of samples to construct train/val/test sets.
        :param train_fraction: Fraction of training examples to load.
        :param val_fraction: Fraction of validation examples to load.
        :param test_fraction: Fraction of test examples to load.
        :param dataloader_params: Parameter dictionary passed to the dataloaders.
        :param augmentors: Augmentor object for providing data augmentation to data samples.
        """
        super().__init__()

        assert train_fraction > 0.0, "Train fraction has to be larger than 0!"
        assert val_fraction > 0.0, "Validation fraction has to be larger than 0!"
        assert test_fraction >= 0.0, "Test fraction has to be larger/equal than 0!"

        # Datasets
        self._train_set: Optional[torch.utils.data.Dataset] = None
        self._val_set: Optional[torch.utils.data.Dataset] = None
        self._test_set: Optional[torch.utils.data.Dataset] = None

        # Feature computation
        self._feature_preprocessor = feature_preprocessor

        # Data splitter train/test/val
        self._splitter = splitter

        # Fractions
        self._train_fraction = train_fraction
        self._val_fraction = val_fraction
        self._test_fraction = test_fraction

        # Data loader for train/val/test
        self._dataloader_params = dataloader_params

        # Extract all samples
        self._all_samples = all_scenarios
        assert len(self._all_samples) > 0, 'No samples were passed to the datamodule'

        # Augmentation setup
        self._augmentors = augmentors

    @property
    def feature_and_targets_builder(self) -> FeaturePreprocessor:
        """Get feature and target builders."""
        return self._feature_preprocessor

    def setup(self, stage: Optional[str] = None) -> None:
        """
        Set up the dataset for each target set depending on the training stage.
        This is called by every process in distributed training.
        :param stage: Stage of training, can be "fit" or "test".
        """
        if stage is None:
            return

        if stage == 'fit':
            # Training Dataset
            train_samples = self._splitter.get_train_samples(self._all_samples)
            assert len(train_samples) > 0, 'Splitter returned no training samples'

            self._train_set = create_dataset(
                train_samples, self._feature_preprocessor, self._train_fraction, "train", self._augmentors
            )

            # Validation Dataset
            val_samples = self._splitter.get_val_samples(self._all_samples)
            assert len(val_samples) > 0, 'Splitter returned no validation samples'

            self._val_set = create_dataset(val_samples, self._feature_preprocessor, self._val_fraction, "validation")
        elif stage == 'test':
            # Testing Dataset
            test_samples = self._splitter.get_test_samples(self._all_samples)
            assert len(test_samples) > 0, 'Splitter returned no test samples'

            self._test_set = create_dataset(test_samples, self._feature_preprocessor, self._test_fraction, "test")
        else:
            raise ValueError(f'Stage must be one of ["fit", "test"], got ${stage}.')

    def teardown(self, stage: Optional[str] = None) -> None:
        """
        Clean up after a training stage.
        This is called by every process in distributed training.
        :param stage: Stage of training, can be "fit" or "test".
        """
        pass

    def train_dataloader(self) -> torch.utils.data.DataLoader:
        """
        Create the training dataloader.
        :raises RuntimeError: If this method is called without calling "setup()" first.
        :return: The instantiated torch dataloader.
        """
        if self._train_set is None:
            raise DataModuleNotSetupError

        return torch.utils.data.DataLoader(
            dataset=self._train_set, **self._dataloader_params, shuffle=True, collate_fn=FeatureCollate()
        )

    def val_dataloader(self) -> torch.utils.data.DataLoader:
        """
        Create the validation dataloader.
        :raises RuntimeError: if this method is called without calling "setup()" first.
        :return: The instantiated torch dataloader.
        """
        if self._val_set is None:
            raise DataModuleNotSetupError

        return torch.utils.data.DataLoader(
            dataset=self._val_set, **self._dataloader_params, collate_fn=FeatureCollate()
        )

    def test_dataloader(self) -> torch.utils.data.DataLoader:
        """
        Create the test dataloader.
        :raises RuntimeError: if this method is called without calling "setup()" first.
        :return: The instantiated torch dataloader.
        """
        if self._test_set is None:
            raise DataModuleNotSetupError

        return torch.utils.data.DataLoader(
            dataset=self._test_set, **self._dataloader_params, collate_fn=FeatureCollate()
        )

    def transfer_batch_to_device(
        self, batch: Tuple[FeaturesType, ...], device: torch.device
    ) -> Tuple[FeaturesType, ...]:
        """
        Transfer a batch to device.
        :param batch: Batch on origin device.
        :param device: Desired device.
        :return: Batch in new device.
        """
        return tuple(move_features_type_to_device(features, device) for features in batch)
