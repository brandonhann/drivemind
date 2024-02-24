import pandas as pd
from fpdf import FPDF


class TrafficOptimizer:
    def __init__(self, traffic_data, green_light_duration=5, yellow_light_duration=3,
                 red_light_duration=3, threshold_good=5, threshold_bad=15,
                 adjustment_factor=1, min_green_duration=3):
        self.traffic_data = traffic_data
        self.green_light_duration = green_light_duration
        self.yellow_light_duration = yellow_light_duration
        self.red_light_duration = red_light_duration
        self.threshold_good = threshold_good
        self.threshold_bad = threshold_bad
        self.adjustment_factor = adjustment_factor
        self.min_green_duration = min_green_duration

    def analyze_traffic(self):
        lane_columns = self.traffic_data.columns[2:]
        total_cars_per_lane = self.traffic_data[lane_columns].sum()
        average_time_per_lane = (
            self.traffic_data[lane_columns].multiply(
                self.traffic_data['Time Detected (seconds)'], axis="index"
            ).sum() / total_cars_per_lane
        )

        congestion_levels = {}
        for lane in lane_columns:
            car_count = total_cars_per_lane.get(lane, 0)
            active_time = average_time_per_lane.get(lane, 0)
            congestion_level = car_count * active_time
            congestion_levels[lane] = congestion_level

        return congestion_levels

    def optimize_traffic_lights(self):
        congestion_levels = self.analyze_traffic()
        optimized_durations = {}

        for lane, congestion_level in congestion_levels.items():
            if congestion_level > self.threshold_good:
                duration_adjustment = self.adjustment_factor
            else:
                duration_adjustment = -self.adjustment_factor
            optimized_durations[lane] = max(
                self.min_green_duration, self.green_light_duration + duration_adjustment)

        return optimized_durations

    def calculate_recommended_durations(self):
        optimized_durations = self.optimize_traffic_lights()
        if optimized_durations:
            average_green_duration = sum(
                optimized_durations.values()) / len(optimized_durations)
            # For simplicity, we keep yellow and red light durations constant in this example
            return average_green_duration, self.yellow_light_duration, self.red_light_duration
        else:
            return self.green_light_duration, self.yellow_light_duration, self.red_light_duration

    def congestion_level_to_category(self, level):
        if level <= self.threshold_good:
            return 'Good', 'green'
        elif level <= self.threshold_bad:
            return 'Medium', 'yellow'
        else:
            return 'Bad', 'red'

    def generate_pdf_report(self, report_path):
        pdf = FPDF()
        pdf.add_page()
        logo_path = 'logotext.png'  # Path to your logo file
        pdf.image(logo_path, x=10, y=8, w=33)
        pdf.set_font("Arial", size=18)
        pdf.cell(200, 10, txt="Traffic Optimization Report", ln=True, align="C")

        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        explanation = "This report analyzes traffic congestion levels and suggests optimizations for traffic light durations."
        pdf.multi_cell(0, 10, explanation, 0, 1)

        configurations = "Initial - Green Light Duration = {0}s, Yellow Light Duration = {1}s, Red Light Duration = {2}s".format(
            self.green_light_duration, self.yellow_light_duration, self.red_light_duration)
        pdf.multi_cell(0, 10, configurations, 0, 1)

        pdf.ln(10)
        congestion_levels = self.analyze_traffic()
        optimized_durations = self.optimize_traffic_lights()

        pdf.cell(90, 10, 'Lane', 1, 0, 'C')
        pdf.cell(40, 10, 'Congestion Level', 1, 0, 'C')
        pdf.cell(60, 10, 'Congestion Category', 1, 1, 'C')

        for lane, level in congestion_levels.items():
            category, color = self.congestion_level_to_category(level)
            if color == 'green':
                pdf.set_fill_color(144, 238, 144)
            elif color == 'yellow':
                pdf.set_fill_color(255, 255, 224)
            elif color == 'red':
                pdf.set_fill_color(255, 160, 122)
            pdf.cell(90, 10, lane, 1, 0, 'C', 1)
            pdf.cell(40, 10, str(round(level, 2)), 1, 0, 'C', 1)
            pdf.cell(60, 10, category, 1, 1, 'C', 1)

        pdf.ln(10)
        conclusion = "The traffic light durations have been optimized based on the analysis to improve traffic flow."
        pdf.multi_cell(0, 5, conclusion, 0, 1)

        # Adding a new analysis section for recommended light durations
        avg_green, avg_yellow, avg_red = self.calculate_recommended_durations()
        analysis_conclusion = "Based on the data analysis, the recommended average durations for optimized traffic flow are: Green Light = {:.2f}s, Yellow Light = {}s, Red Light = {}s.".format(
            avg_green, avg_yellow, avg_red)
        pdf.multi_cell(0, 10, analysis_conclusion, 0, 1)

        pdf.output(report_path)


# Example usage
file_path = 'car_detections.csv'
traffic_data = pd.read_csv(file_path)
optimizer = TrafficOptimizer(traffic_data)
report_path = 'TrafficOptimizationReport.pdf'
optimizer.generate_pdf_report(report_path)
