from miro.objects.base_miro_object import BaseMiroObject, MiroObjectType

# class Style:
#     def __init__(self, **kwargs):
#         self.attributes=kwargs


class Widget(BaseMiroObject):

    def __init__(self, **kwargs):
        super().__init__(kwargs['obj_id'], kwargs['obj_type'])
        #self.obj_id = kwargs['obj_id']
        #self.obj_type = kwargs['obj_type']
        self.capabilities = kwargs['capabilities'] if 'capabilities' in kwargs else {}
        # required to store metadata
        self.app_id = kwargs['app_id'] if 'app_id' in kwargs else '0'
        if 'metadata' in kwargs:
            # metadata is returned as { 'app_id': { real metadata } }
            m = kwargs['metadata']

            if len(m) == 1:
                # looks like miro format with app_id and not a real dictionary
                # the question remains whether we should override app_id, but I guess yes
                self.app_id = list(m)[0] # first and only value of keys is app_id
                self.metadata = list(m.values())[0] # actual dict of metadata
            else:
                # we assume the caller knows what he/she is doing
                self.metadata = m
        else:
           self.metadata = {}

        self.style = kwargs['style'] if 'style' in kwargs else {}

    def attributes2miro(self, api_version = '1'):
        data = { }
        if self.obj_id and self.obj_id!='0':
            data['id']=self.obj_id

        if self.metadata:
            data['metadata']=self.metadata

        if self.style:
            data['style']=self.style

        if api_version == '1':
            data['type'] = self.obj_type
        elif api_version == '2':
            data['data'] = { 'type': self.obj_type }
        else:
            # ?
            pass

        return data

    def endpoint_name(self, api_version = '1'):
        raise NameError(f'The method endpoint_name should have been redefined in the class {self}')

class Shape(Widget):

    def __init__(self, **kwargs):
        params=dict(kwargs)
        params['obj_type'] = MiroObjectType.SHAPE
        super().__init__(**params)
        self.text = kwargs['text'] if 'text' in kwargs else 'Noname'
        self.x_pos = kwargs['x_pos'] if 'x_pos' in kwargs else 0
        self.y_pos = kwargs['y_pos'] if 'y_pos' in kwargs else 0
        self.width = kwargs['width'] if 'width' in kwargs else 0
        self.height = kwargs['height'] if 'height' in kwargs else 0
        self.rotation = kwargs['rotation'] if 'rotation' in kwargs else 0  # number of degrees clockwise


    def attributes2miro(self, api_version = '1'):
        data = super().attributes2miro(api_version)
        if api_version == '1':
            data['type'] = self.obj_type
            data['text']=self.text
            data['x']=self.x_pos
            data['y']=self.y_pos
            if self.metadata:
                data['metadata'] = { self.app_id: self.metadata }
        elif api_version == '2':
            d = data['data'] if 'data' in data else {}
            d['content'] = self.text
            # not supported for now
            # data['geometry'] = { 'width':self.width, 'height': self.height }
            data['position'] = { 'x': self.x_pos, 'y': self.y_pos }
        else:
            # ?
            pass
        

        
        # data['mindmap'] =  {
        #    "theme": "colorBranch",
        #     "layout": "butterfly"
        # }
        return data

    def endpoint_name(self, api_version = '1'):
        if api_version == '1':
            return 'widgets'
        return 'shapes'
        
class Text(Shape):
    def __init__(self, **kwargs):
        params=dict(kwargs)
        params['obj_type'] = MiroObjectType.TEXT
        super().__init__(**params)

    def endpoint_name(self, api_version = '1'):
        if api_version == '1':
            return 'widgets'
        return 'texts'

    def attributes2miro(self, api_version = '1'):
        data = super().attributes2miro(api_version)
        data['type']='text'

        #data['mindmap'] = { "mindmap": { "theme": "colorBranch", "layout": "butterfly" } }
        return data

class Line(Widget):
    def __init__(self, **kwargs):
        params=dict(kwargs)
        params['obj_type'] = MiroObjectType.LINE
        super().__init__(**params)
        self.start_widget_id = kwargs['start_widget_id']
        self.end_widget_id = kwargs['end_widget_id']

    def attributes2miro(self, api_version = '1'):
        data = super().attributes2miro(api_version)
        #w1=Shape(obj_id=self.start_widget_id,
        #    #these parameters are not really needed
        #    text='temp', x_pos=0, y_pos=0, width=1, height=1, rotation=0)
        data['startWidget']={ 'id': self.start_widget_id }
        #w2=Shape(obj_id=self.end_widget_id,
        #    #these parameters are not really needed
        #    text='temp', x_pos=0, y_pos=0, width=1, height=1, rotation=0)
        data['endWidget']={ 'id': self.end_widget_id }
        return data

    def endpoint_name(self, api_version = '1'):
        if api_version == '1':
            return 'widgets'
        return 'lines'


class MiroAttributeMapper:
    # maps object attributes to their location in JSON structures
    # based on API version
    MIRO_OBJID = 'id'
    MIRO_TYPE = 'type'
    MIRO_X = 'x'
    MIRO_Y = 'y'
    MIRO_WIDTH = 'width'
    MIRO_HEIGHT = 'heiht'
    MIRO_ROTATION = 'rotation'
    MIRO_TEXT = 'text'
    MIRO_STYLE = 'style'
    MIRO_METADATA = 'metadata'
   
    attribute_map = {
        '1': { # easy - mostly flat list
            MIRO_OBJID: [ MIRO_OBJID ],
            MIRO_TYPE: [ MIRO_TYPE ],
            MIRO_X: [ MIRO_X ],
            MIRO_Y: [ MIRO_Y ],
            MIRO_WIDTH: [ MIRO_WIDTH ],
            MIRO_HEIGHT: [ MIRO_HEIGHT ],
            MIRO_ROTATION: [ MIRO_ROTATION ],
            MIRO_TEXT: [ MIRO_TEXT ],
            MIRO_METADATA: [ MIRO_METADATA ]
            },
        '2': {}
        }

    @staticmethod
    def extract_by_path(d:dict, path: list ) -> str:
        """ Extract value of a nested dict (JSON structure) by it's path,
        e.g. extract_by_path( { 'person_data':{ 'first_name': 'John', 'last_name': 'Doe' }},
        ['person_data', 'first_name']) returns 'Doe' """
        
        p=path[0]
        #for z in d.keys():
        #    print(f'{z} == {p} equals to ', z==p, "\n")
        is_there = p in d
        #print('Extract from ', type(d), d, 'by path', path,'---', p, type(p), "\n", d.keys(), 'is in there', p in d, is_there, "\n") 
 
        if is_there:
            x = d[p]
            remaining_path = path[1:]
            if len(remaining_path) == 0:
                # we found the required element
                return x
            elif type(x) is dict:
                return extract_by_path(x, remaining_path)
            else:
                # mismatch of path and data?
                print('weird ', remaining_path, x)
                return ''
        # no such element
        return ''
    
    @staticmethod
    def extract_attribute(data: dict, attr: str, api_version = '1') -> str:
        attributes = MiroAttributeMapper.attribute_map[api_version]
        path = attributes[attr]
        return MiroAttributeMapper.extract_by_path(data, path)

    @staticmethod
    def create_widget_by_type(widget_json, api_version = '1') -> Widget:
        widget_type = MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_TYPE, api_version)
        if widget_type == MiroObjectType.SHAPE:
            return Shape(obj_id=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_OBJID, api_version),
                        text=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_TEXT, api_version),
                        metadata=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_METADATA, api_version),
                        x_pos=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_X, api_version),
                        y_pos=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_Y, api_version),
                        width=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_WIDTH, api_version),
                        height=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_HEIGHT, api_version),
                        rotation=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_ROTATION, api_version))
        elif widget_type == MiroObjectType.LINE:
            return Line(obj_id=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_OBJID, api_version),
                        start_widget_id=widget_json['startWidget']['id'],
                        end_widget_id=widget_json['endWidget']['id'])
        elif widget_type == MiroObjectType.TEXT:
            return Text(obj_id=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_OBJID, api_version),
                        text=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_TEXT, api_version),
                        metadata=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_METADATA, api_version),
                        x_pos=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_X, api_version),
                        y_pos=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_Y, api_version),
                        width=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_WIDTH, api_version),
                        height=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_HEIGHT, api_version),
                        rotation=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_ROTATION, api_version))
        return Widget(obj_id=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_OBJID, api_version),
                        metadata=MiroAttributeMapper.extract_attribute(widget_json, MiroAttributeMapper.MIRO_METADATA, api_version))

    def produce_widget(widget_json, api_version = '1') -> Widget:
        return MiroAttributeMapper.create_widget_by_type(widget_json, api_version)