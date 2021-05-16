from vector_control import volume_controller as vc

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Column
from bokeh.io import curdoc
from bokeh.events import DoubleTap


def callback(event):
	Coords=(event.x,event.y)
	coordList.append(Coords)
	source.data = dict(x=[i[0] for i in coordList], y=[i[1] for i in coordList])

def plot_bokeh() :
bound = 10
p = figure(title='Double click to leave a dot.',
		   tools=TOOLS,width=700,height=700,
		   x_range=(-bound, bound), y_range=(-bound, bound))

source = ColumnDataSource(data=dict(x=[], y=[]))
p.circle(source=source,x='x',y='y')

#add a dot where the click happened

p.on_event(DoubleTap, callback)

layout=Column(p)


def main() :
	device_settings={"Titan":{"location":np.array([12,15])}, #1
				"janus":{"location":np.array([6,1])}, #2
				"Kitchen speaker":{"location":np.array([20,1])}, #3
				"Epimetheus":{"location":np.array([3,12])} #4
				# "Bedroom":[[9,22],15] #5
	}


	controller=volume_controller(device_settings, foci=foci	)



if __name__ == "__main__":
	# execute only if run as a script
	main()
