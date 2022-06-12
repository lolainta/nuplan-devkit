from collections import defaultdict
from typing import Dict, List, Optional, Type

from nuplan.common.maps.maps_datatypes import TrafficLightStatusData, TrafficLightStatusType
from nuplan.planning.scenario_builder.abstract_scenario import AbstractScenario
from nuplan.planning.simulation.history.simulation_history_buffer import SimulationHistoryBuffer
from nuplan.planning.simulation.observation.abstract_observation import AbstractObservation
from nuplan.planning.simulation.observation.idm.idm_agent_manager import IDMAgentManager
from nuplan.planning.simulation.observation.idm.idm_agents_builder import build_idm_agents_on_map_rails
from nuplan.planning.simulation.observation.observation_type import DetectionsTracks, Observation
from nuplan.planning.simulation.simulation_time_controller.simulation_iteration import SimulationIteration


class IDMAgents(AbstractObservation):
    """
    Simulate agents based on IDM policy.
    """

    def __init__(
        self,
        target_velocity: float,
        min_gap_to_lead_agent: float,
        headway_time: float,
        accel_max: float,
        decel_max: float,
        scenario: AbstractScenario,
        minimum_path_length: float = 20,
        planned_trajectory_samples: int = 6,
        planned_trajectory_sample_interval: float = 0.5,
    ):
        """
        Constructor for IDMAgents

        :param target_velocity: [m/s] Desired velocity in free traffic
        :param min_gap_to_lead_agent: [m] Minimum relative distance to lead vehicle
        :param headway_time: [s] Desired time headway. The minimum possible time to the vehicle in front
        :param accel_max: [m/s^2] maximum acceleration
        :param decel_max: [m/s^2] maximum deceleration (positive value)
        :param scenario: scenario
        :param minimum_path_length: [m] The minimum path length
        :param planned_trajectory_samples: number of elements to sample for the planned trajectory.
        :param planned_trajectory_sample_interval: [s] time interval of sequence to sample from.
        """
        self.current_iteration = 0

        self._target_velocity = target_velocity
        self._min_gap_to_lead_agent = min_gap_to_lead_agent
        self._headway_time = headway_time
        self._accel_max = accel_max
        self._decel_max = decel_max
        self._scenario = scenario
        self._minimum_path_length = minimum_path_length
        self._planned_trajectory_samples = planned_trajectory_samples
        self._planned_trajectory_sample_interval = planned_trajectory_sample_interval

        # Prepare IDM agent manager
        self._idm_agent_manager: Optional[IDMAgentManager] = None

    def reset(self) -> None:
        """Inherited, see superclass."""
        self.current_iteration = 0
        self._idm_agent_manager = None

    def _get_idm_agent_manager(self) -> IDMAgentManager:
        """
        Create idm agent manager in case it does not already exists
        :return: IDMAgentManager
        """
        if not self._idm_agent_manager:
            agents, agent_occupancy = build_idm_agents_on_map_rails(
                self._target_velocity,
                self._min_gap_to_lead_agent,
                self._headway_time,
                self._accel_max,
                self._decel_max,
                self._minimum_path_length,
                self._scenario,
            )
            self._idm_agent_manager = IDMAgentManager(agents, agent_occupancy, self._scenario.map_api)

        return self._idm_agent_manager

    def observation_type(self) -> Type[Observation]:
        """Inherited, see superclass."""
        return DetectionsTracks  # type: ignore

    def initialize(self) -> None:
        """Inherited, see superclass."""
        pass

    def get_observation(self) -> DetectionsTracks:
        """Inherited, see superclass."""
        detections = self._get_idm_agent_manager().get_active_agents(
            self.current_iteration, self._planned_trajectory_samples, self._planned_trajectory_sample_interval
        )
        return detections

    def update_observation(
        self, iteration: SimulationIteration, next_iteration: SimulationIteration, history: SimulationHistoryBuffer
    ) -> None:
        """Inherited, see superclass."""
        self.current_iteration = next_iteration.index
        tspan = next_iteration.time_s - iteration.time_s
        traffic_light_data: List[TrafficLightStatusData] = self._scenario.get_traffic_light_status_at_iteration(
            self.current_iteration
        )

        # Extract traffic light data into Dict[traffic_light_status, lane_connector_ids]
        traffic_light_status: Dict[TrafficLightStatusType, List[str]] = defaultdict(list)

        for data in traffic_light_data:
            traffic_light_status[data.status].append(str(data.lane_connector_id))

        ego_state, _ = history.current_state
        self._get_idm_agent_manager().propagate_agents(ego_state, tspan, self.current_iteration, traffic_light_status)
