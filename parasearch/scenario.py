import sys
import numpy as np
import math
import xml.etree.ElementTree as ET
import gym_lass.lass as Lass
from utils.utils import Utils
from gym_lass.vehicles import CarMOBIL
from gym_lass.algos import IDM, MOBIL

ego_controller = ET.XML( \
    '''
    <ObjectController>
        <Controller name="IDMController">
            <Properties>
                <Property name="esminiController" value="ExternalController"/>
                <Property name="baseController" value="Naive"/>
            </Properties>
        </Controller>
    </ObjectController>
    ''')

ego_sensor = ET.XML( \
    '''
    <ObjectSensor>
        <Sensor name="IdealSensor">
            <Properties>
                <Property name="sensorType" value="IdealSensor" x="2" y="0" z="1" h="0" rangeNear="0" rangeFar="20"
                        fovH="0.3491" maxObj="10"/>
            </Properties>
        </Sensor>
        <Sensor name="LaneSensor">
            <Properties>
                <Property name="sensorType" value="LaneSensor" lookaheadDistance="5" lookaheadMode="0"/>
            </Properties>
        </Sensor>
        <Sensor name="RoadSensor">
            <Properties>
                <Property name="sensorType" value="RoadSensor"/>
            </Properties>
        </Sensor>
    </ObjectSensor>
    ''')

controller_enable_action = ET.XML( \
    '''
    <PrivateAction>
            <ActivateControllerAction longitudinal="false" lateral="false"/>
    </PrivateAction>
    ''')


class ScenarioFalsification:

    def __init__(self, xosc_path):
        self.__xosc = ET.parse(xosc_path).getroot()
        mins = list()
        maxs = list()
        self.__adjParas = list()
        for para in self.__xosc.findall('./ParameterDeclarations/ParameterDeclaration'):
            if 'name' in para.attrib and para.attrib['name'].startswith('MG-'):
                # Maneuver Group Trigger Time
                self.__adjParas.append(para)
                mins.append(float(para.attrib['min']))
                maxs.append(float(para.attrib['max']))

        for obj in self.__xosc.findall('./Entities/ScenarioObject'):
            if 'name' in obj.attrib and obj.attrib['name'] == 'ego':
                obj.append(ego_controller)
                obj.append(ego_sensor)
            break

        for priv in self.__xosc.findall('./Storyboard/Init/Actions/Private'):
            if 'entityRef' in priv and priv.attrib['entityRef'] == 'ego':
                priv.append(controller_enable_action)
            break

        self.__mins = np.array(mins)
        self.__maxs = np.array(maxs)

    @property
    def mins(self):
        return self.__mins

    @property
    def maxs(self):
        return self.__maxs

    def run(self, parameters, display=False, record=False):
        for i in range(len(parameters)):
            self.__adjParas[i].attrib['value'] = str(parameters[i])

        lass = Lass.Lass(ET.tostring(self.__xosc, encoding='unicode', method='xml'), display, record)
        vdict = lass.vehicleDict()
        s = lass.observe()
        ego_id = [k for k, v in vdict.items() if v == "ego"][0]
        ego = CarMOBIL(ego_id, s[ego_id], IDM(25, 1, 1.5, 3, 1.6), MOBIL(20, 0.2, 0.5))
        t = 2000
        min_gap = float('inf')
        is_rear = False
        is_side = False
        is_blamed = False
        while t:
            perception = lass.perceive()
            a = ego.get_action(perception[ego_id], s)
            if a is None:
                # TODO: 未知原因, RoadSensor未获取到信息, 且仅在display=False时表现
                # 临时解决方案: 将action设置为[0, 0]走一步
                s, col, q, info = lass.step({0: [0,0]})
                # print('No action')
                # return False, None, None, None
            else:
                s, col, q, info = lass.step({0: a})
            ego.update_state(s[ego_id])

            # collision detection
            if len(col[ego_id]) > 0:
                min_gap = 0
                # check responsibility of collision
                bumper_id = col[ego_id][0]
                # print(bumper_id)
                delta_t = math.fabs(s[ego_id].t - s[bumper_id].t)
                width = (s[ego_id].width + s[bumper_id].width) / 2
                if delta_t < width:
                    # rear collision
                    is_rear = True
                    if s[ego_id].s < s[bumper_id].s:
                        is_blamed = True
                else:
                    # side collision
                    is_side = True
                    # if math.fabs(s[ego_id].h) > math.fabs(s[bumper_id].h):
                    #     is_blamed = True
                    if math.fabs(s[ego_id].lane_offset) > math.fabs(s[bumper_id].lane_offset):
                        is_blamed = True

                break
            other_col = []
            for i in range(len(col)):
                if i == ego_id:
                    continue
                other_col += col[i]
            if len(col[ego_id]) == 0 and len(other_col) > 0:
                # branch cut
                return None, False, False, False, info['t']

            # calculate gap
            gaps = [Utils.gap(s[ego_id], s[i]) for i in range(len(s)) if i != ego_id]
            min_gap = min(min(gaps), min_gap)

            if q:
                # print('scenario is finished: {}'.format(t))
                break
            t -= 1

        # print('min_gap: {}'.format(min_gap))
        # print(min_gap, is_rear, is_side, is_blamed, info['t'])
        return min_gap, is_rear, is_side, is_blamed, info['t']

    def dump(self, parameters, filename):
        for i in range(len(parameters)):
            self.__adjParas[i].attrib['value'] = str(parameters[i])

        xosc = ET.ElementTree(self.__xosc)
        xosc.write(filename, encoding="unicode", method="xml")


class ScenarioTest:

    def __init__(self, xosc_path):
        self.__xosc = ET.parse(xosc_path).getroot()
        mins = list()
        maxs = list()
        self.__adjParas = list()
        self.__holdParas = list()
        for para in self.__xosc.findall('./ParameterDeclarations/ParameterDeclaration'):
            if 'name' in para.attrib and para.attrib['name'].endswith('-EGO'):
                # Maneuver Group Trigger Time
                self.__adjParas.append(para)
                mins.append(float(para.attrib['min']))
                maxs.append(float(para.attrib['max']))
            elif 'name' in para.attrib and para.attrib['name'].startswith('MG-'):
                self.__holdParas.append(para)

        self.__mins = np.array(mins)
        self.__maxs = np.array(maxs)

    @property
    def mins(self):
        return self.__mins

    @property
    def maxs(self):
        return self.__maxs

    def set_hold_parameters(self, parameters):
        for i in range(len(parameters)):
            self.__holdParas[i].attrib['value'] = str(parameters[i])

    def run(self, parameters, display=False, record=False):
        for i in range(len(parameters)):
            self.__adjParas[i].attrib['value'] = str(parameters[i])

        lass = Lass.Lass(ET.tostring(self.__xosc, encoding='unicode', method='xml'), display, record)
        t = 2000
        min_gap = float('inf')
        while t:
            vdict = lass.vehicleDict()
            ego_id = [k for k, v in vdict.items() if v == "ego"][0]
            s, col, q, _ = lass.step({})

            # collision detection
            if len(col[ego_id]) > 0:
                min_gap = 0
                break
            other_col = []
            for i in range(len(col)):
                if i == ego_id:
                    continue
                other_col += col[i]
            if len(col[ego_id]) == 0 and len(other_col) > 0:
                # branch cut
                return None

            # calculate gap
            gaps = [Utils.gap(s[ego_id], s[i]) for i in range(len(s)) if i != ego_id]
            min_gap = min(min(gaps), min_gap)

            if q:
                # print('scenario is finished: {}'.format(t))
                break
            t -= 1

        # print('min_gap: {}'.format(min_gap))

        return min_gap

    def dump(self, parameters, filename):
        for i in range(len(parameters)):
            self.__adjParas[i].attrib['value'] = str(parameters[i])

        xosc = ET.ElementTree(self.__xosc)
        xosc.write(filename, encoding="unicode", method="xml")
