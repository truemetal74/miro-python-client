from miro.objects.base_miro_object import BaseMiroObject, MiroObjectType

# class Style:
#     def __init__(self, **kwargs):
#         self.attributes=kwargs

class Widget(BaseMiroObject):

    def __init__(self, obj_id: str,
                 obj_type=MiroObjectType.WIDGET):
        super().__init__(obj_id, obj_type)
        self.obj_id = obj_id
        self.obj_type = obj_type
        self.capabilities = dict()
        self.metadata = dict()


    def attributes2miro(self):
        data = {
            'type': self.obj_type
        }
        if self.obj_id and self.obj_id!='0':
            data['id']=self.obj_id
        if self.metadata:
            data['metadata']=self.metadata

        return data

class Shape(Widget):

    def __init__(self, obj_id: str, text: str,
                 x_pos: float, y_pos: float,
                 width: float, height: float,
                 rotation: float):
        super().__init__(obj_id, MiroObjectType.SHAPE)
        self.text = text
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.rotation = rotation  # number of degrees clockwise
        self.style = dict()

    def attributes2miro(self):
        data = super().attributes2miro()
        data['type'] = 'text'
        data['text']=self.text
        data['x']=self.x_pos
        data['y']=self.y_pos
        if self.style:
            data['style']=self.style
        return data

class Line(Widget):

    def __init__(self, obj_id: str,
                 start_widget_id: str,
                 end_widget_id: str):
        super().__init__(obj_id, MiroObjectType.LINE)
        self.start_widget_id = start_widget_id
        self.end_widget_id = end_widget_id

    def attributes2miro(self):
        data = super().attributes2miro()
        #w1=Shape(obj_id=self.start_widget_id,
        #    #these parameters are not really needed
        #    text='temp', x_pos=0, y_pos=0, width=1, height=1, rotation=0)
        data['startWidget']={ 'id': self.start_widget_id }
        #w2=Shape(obj_id=self.end_widget_id,
        #    #these parameters are not really needed
        #    text='temp', x_pos=0, y_pos=0, width=1, height=1, rotation=0)
        data['endWidget']={ 'id': self.end_widget_id }
        return data