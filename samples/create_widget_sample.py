from miro.client import MirApiClient
from miro.utils import get_auth_token_from_env

client = MiroApiClient(base_url='https://api.miro.com',
                       api_version=1, debug=True,
                       auth_token=get_auth_token_from_env())

#widgets = client.get_all_widgets_by_board_id('o9J_kwX5tTk=')
#for widget in widgets:
#    print(widget)

w1 = Shape(obj_id=0, text="Sample Widget",
        x_pos=10,y_pos=10,width=100,height=100,rotation=0)
w1.style = {
          "backgroundOpacity":1.0,
            "backgroundColor":'#ffffff',
            "borderColor":'#7a28ff',
            "borderStyle":"normal",
            "borderOpacity":1.0,
            "borderWidth":2.0,
            "fontSize":14,
            "fontFamily":"OpenSans",
            "textColor":"#1a1a1a",
            "textAlign":"center",
            "shapeType":"pill"
    }
print("style=", w1.style)
new_w1 = miro.add_widget(board_id, w1)
print("Created widget for ", new_w1)
