class VRResolver:
    def __init__(self, boolArrayVR, boolArray, intArrayVR, intArray, realArrayVR, realArray, stringArrayVR=None, stringArray=None):
        self.boolArrayVR = [int(v) for v in boolArrayVR]
        self.boolArray = boolArray
        self.intArrayVR = [int(v) for v in intArrayVR]
        self.intArray = intArray
        self.realArrayVR = [int(v) for v in realArrayVR]
        self.realArray = realArray
        self.stringArrayVR = [int(v) for v in stringArrayVR] if stringArrayVR else []
        self.stringArray = stringArray if stringArray else []


    def getValueByVR(self, vr_id, vr_list, value_list):
        try:
            index = [int(v) for v in vr_list].index(int(vr_id))
            return value_list[index]
        except ValueError:
            raise ValueError(f"VR {vr_id} não encontrado na lista VR.")

    def get_bool_by_vr(self,vr_id):
        return self.getValueByVR(vr_id, self.boolArrayVR, self.boolArray)

    def get_int_by_vr(self,vr_id):
        return self.getValueByVR(vr_id, self.intArrayVR, self.intArray)

    def get_real_by_vr(self,vr_id):
        return self.getValueByVR(vr_id, self.realArrayVR, self.realArray)

    def get_string_by_vr(self,vr_id):
        return self.getValueByVR(vr_id, self.stringArrayVR, self.stringArray)