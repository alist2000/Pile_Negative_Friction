import pandas as pd
import plotly.graph_objects as go
import numpy as np


# Function to calculate intersection
def intersection(depth, curve_a, curve_b):
    # Convert the data to numpy arrays for processing
    depth = np.array(depth)
    curve_a = np.array(curve_a)
    curve_b = np.array(curve_b)

    # Find the points just before and after where curve_a crosses curve_b
    for i in range(len(depth) - 1):
        if (curve_a[i] - curve_b[i]) * (curve_a[i + 1] - curve_b[i + 1]) < 0:
            # Linear interpolation for more accurate intersection point
            # (x - x0) / (x1 - x0) = (y - y0) / (y1 - y0)
            # Solve for x (depth here) when y (curve_a and curve_b here) are equal
            depth_intersect = (depth[i] * (curve_b[i + 1] - curve_a[i + 1]) + depth[i + 1] * (
                    curve_a[i] - curve_b[i])) / (curve_b[i + 1] - curve_a[i + 1] + curve_a[i] - curve_b[i])
            curve_intersect = curve_a[i] + (curve_a[i + 1] - curve_a[i]) * (depth_intersect - depth[i]) / (
                    depth[i + 1] - depth[i])
            return depth_intersect, curve_intersect

    return None, None  # Return None if there is no intersection


class Plot:
    def __init__(self, depth, curve_a, curve_b):
        self.depth = depth
        self.curve_a = curve_a
        self.curve_b = curve_b

        # Define the lines as pandas DataFrame
        df = pd.DataFrame({'x': depth, 'y1': curve_a, 'y2': curve_b})

        # Calculate the intersection point
        depth_intersect, curve_intersect = intersection(df['x'], df['y1'], df['y2'])

        layout = go.Layout(
            title='Effective negative friction length',
            xaxis=dict(title=''),
            yaxis=dict(title='Pile Length', autorange='reversed'),
            showlegend=True,
        )
        # Create the figure
        fig = go.Figure(layout=layout)

        # Add the first line
        fig.add_trace(go.Scatter(x=df['y1'], y=df['x'], mode='lines', name='Curve A'))

        # Add the second line
        fig.add_trace(go.Scatter(x=df['y2'], y=df['x'], mode='lines', name='Curve B'))

        # Add the intersection point as a marker if it exists
        if depth_intersect is not None and curve_intersect is not None:
            fig.add_trace(go.Scatter(x=[curve_intersect], y=[depth_intersect], mode='markers', name='Intersection'))
            intersection_annotation = f'Depth {depth_intersect:.2f}'
            fig.add_annotation(x=curve_intersect, y=depth_intersect, text=intersection_annotation, showarrow=True,
                               arrowhead=1)
            print(intersection_annotation)  # Report the depth of intersection

        # Update layout to show the end of the depth on the y-axis
        fig.update_layout(
            title='Effective negative friction length',
            xaxis=dict(title=''),
            yaxis=dict(title='Pile Length', autorange='reversed'),
            showlegend=True,
        )

        # Show the figure
        fig.show()
        fig.write_html("plot.html")
        fig.write_image("plot.png")
        self.effective_depth = depth_intersect

# # Example usage:
# depth = [1, 2, 3, 4, 5]
# curve_a = [10, 14, 18, 24, 30]
# curve_b = [5, 8, 12, 18, 25]
# plot = Plot(depth, curve_a, curve_b)
