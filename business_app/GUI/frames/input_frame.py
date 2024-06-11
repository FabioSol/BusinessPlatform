from business_app.GUI.frames.base_frame import BaseFrame
from business_app.GUI.frames.subframes.input_subframes import sub_frames_dict

class InputFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, sub_frames_dict, **kwargs)
