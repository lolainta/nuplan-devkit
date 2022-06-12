from typing import Any, Dict

from nuplan.common.maps.abstract_map import SemanticMapLayer

MOTIONAL_PALETTE: Dict[str, str] = {
    "motional_purple": "#5C48F6",
    "hyundai_blue": "#0A2972",
    "navy": "#030A14",
    "medium_asphalt": "#828791",
    "light_asphalt": "#D2DCDC",
    "dark_asphalt": "#40444A",
    "solid_aqua": "#00f6ff",
}

PLOT_PALETTE: Dict[str, str] = {
    "font_lavender_gray": "#adb9e3",
    "font_white": "#c9eaf1",
    "background_white": "#fafafa",
    "background_black": "#000000",
    "chart_green": "#00FF73",
    "chart_yellow": "#E2FF1A",
}

default_data_table: Dict[str, Any] = {'row_height': 80}

default_multi_choice_style: Dict[str, Any] = {'option_limit': 10}

default_spinner_style: Dict[str, Any] = {'width': 300, 'low': 1}
default_div_style: Dict[str, Any] = {'margin': (5, 5, 5, 30)}
base_tab_style: Dict[str, Any] = {
    "plot_sizes": (350, 350),
    "plot_frame_sizes": (1200, 1200),
    "search_criteria_sizes": (80, 80),
}

simulation_tile_style: Dict[str, Any] = {
    "figure_sizes": (600, 600),
    "figure_margins": [10, 20, 20, 50],
    "figure_title_text_font_size": "10pt",
    "video_button_margins": [10, 20, 20, 50],  # Top, right, bottom, left
    "slider_margins": [10, 20, 10, 50],
    "background_color": "#000000",
    "mission_goal_color": "#00FF00",
    "mission_goal_alpha": 0.0,
    "mission_goal_line_width": 2,
}

simulation_tile_trajectory_style: Dict[str, Any] = {
    "ego": {"line_color": "#00C8C8", "line_alpha": 0.8, "line_width": 2},
    "expert_ego": {"line_color": "#FA9600", "line_alpha": 0.8, "line_width": 2},
}

simulation_tile_agent_style: Dict[str, Any] = {
    "ego": {"fill_color": "#FFFFFF", "fill_alpha": 1.0, "line_color": "#808080", "line_width": 2},
    "vehicles": {"fill_color": "#84E573", "fill_alpha": 0.5, "line_color": "#84E573", "line_width": 1},
    "pedestrians": {"fill_color": "#4D83E1", "fill_alpha": 0.5, "line_color": "#4D83E1", "line_width": 1},
    "bicycles": {"fill_color": "#FF4D4D", "fill_alpha": 0.5, "line_color": "#FF4D4D", "line_width": 1},
    "genericobjects": {"fill_color": "#AE4DFF", "fill_alpha": 0.5, "line_color": "#AE4DFF", "line_width": 1},
    "traffic_cone": {"fill_color": "#FF9D4D", "fill_alpha": 0.5, "line_color": "#FF9D4D", "line_width": 1},
    "barrier": {"fill_color": "#FFCC4D", "fill_alpha": 0.5, "line_color": "#FFCC4D", "line_width": 1},
    "czone_sign": {"fill_color": "#00f6ff", "fill_alpha": 0.5, "line_color": "#00f6ff", "line_width": 1},
}

simulation_map_layer_color: Dict[SemanticMapLayer, Any] = {
    SemanticMapLayer.LANE: {"fill_color": "#4D6680", "fill_color_alpha": 0.5, "line_color": "#2d3ea7"},
    SemanticMapLayer.WALKWAYS: {"fill_color": "#7e772e", "fill_color_alpha": 0.5, "line_color": "#7e772e"},
    SemanticMapLayer.CARPARK_AREA: {"fill_color": "#ff7f00", "fill_color_alpha": 0.5, "line_color": "#ff7f00"},
    SemanticMapLayer.PUDO: {"fill_color": "#AF75A7", "fill_color_alpha": 0.3, "line_color": "#AF75A7"},
    SemanticMapLayer.INTERSECTION: {"fill_color": "#7C8691", "fill_color_alpha": 0.5, "line_color": "#2d3ea7"},
    SemanticMapLayer.STOP_LINE: {"fill_color": "#FF0101", "fill_color_alpha": 0.5, "line_color": "#FF0101"},
    SemanticMapLayer.CROSSWALK: {"fill_color": "#B5B5B5", "fill_color_alpha": 0.3, "line_color": "#B5B5B5"},
    SemanticMapLayer.BASELINE_PATHS: {"line_color": "#CBCBCB", "line_color_alpha": 1.0},
    SemanticMapLayer.LANE_CONNECTOR: {"line_color": "#CBCBCB", "line_color_alpha": 1.0},
}

configuration_tab_style: Dict[str, Any] = {
    "file_path_input_margin": [15, 0, 50, 30],
    "folder_path_selection_margin": [12, 0, 0, 6],
    "main_board_layout_height": 600,
}

histogram_tab_style: Dict[str, Any] = {
    "statistic_figure_margin": [10, 20, 20, 30],
    "statistic_figure_title_text_font_size": "8pt",
    "statistic_figure_xaxis_axis_label_text_font_size": "8pt",
    "statistic_figure_xaxis_major_label_text_font_size": "8pt",
    "statistic_figure_yaxis_axis_label_text_font_size": "8pt",
    "statistic_figure_yaxis_major_label_text_font_size": "8pt",
    "histogram_title_div_margin": [30, 0, 10, 30],
    "quad_line_color": "white",
    "quad_alpha": 0.5,
    "quad_line_width": 3,
    "pdf_alpha": 0.7,
    "pdf_line_width": 4,
    "cdf_alpha": 0.7,
    "cdf_line_width": 2,
    "plot_legend_background_fill_alpha": 0.3,
    "plot_legend_label_text_font_size": "8pt",
    "plot_yaxis_axis_label": "Frequency",
    "plot_grid_line_color": "white",
}

overview_tab_style: Dict[str, Any] = {
    "table_margins": [20, 0, 0, 50],
    "table_width": 800,
    "table_height": 300,
    "scatter_size": 10,
    "statistic_figure_margin": [10, 20, 20, 30],
    "plot_legend_background_fill_alpha": 0.3,
    "plot_grid_line_color": "white",
    "overview_title_div_margin": [10, 20, 20, 30],
}

scenario_tab_style: Dict[str, Any] = {
    "time_series_figure_margins": [10, 20, 20, 30],
    "time_series_figure_title_text_font_size": "8pt",
    "time_series_figure_xaxis_axis_label_text_font_size": "9pt",
    "time_series_figure_xaxis_major_label_text_font_size": "9pt",
    "time_series_figure_yaxis_axis_label_text_font_size": "9pt",
    "time_series_figure_yaxis_major_label_text_font_size": "9pt",
    "time_series_figure_xaxis_axis_label": "frame",
    "plot_legend_label_text_font_size": "8pt",
}
