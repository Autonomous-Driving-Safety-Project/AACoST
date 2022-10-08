from scenariogeneration import xosc

ROADID = 20


class OSCGen:
    def __init__(self, template_path, ref_speed, ref_position):
        self.__scenario = xosc.ParseOpenScenario(template_path)
        self.__ref_speed = ref_speed
        self.__ref_position = ref_position
        self.__maneuver_group_index = 0
        self.__scenario.storyboard.add_act(xosc.Act('ScenarioAct'))

    def add_entity(self, entity_name, catalog_ref, position, lane, speed):
        entity_ref = xosc.utils.CatalogReference('VehicleCatalog', catalog_ref)
        self.__scenario.entities.add_scenario_object(entity_name, entity_ref)
        entity_para = xosc.utils.Parameter('owner', xosc.ParameterType.string, entity_name)
        init_teleport_action = xosc.actions.TeleportAction(
            xosc.position.LanePosition(self.__ref_position + position, 0, lane, ROADID))
        init_speed_action = xosc.actions.AbsoluteSpeedAction(self.__ref_speed + speed,
                                                             xosc.TransitionDynamics(xosc.DynamicsShapes.step,
                                                                                     xosc.DynamicsDimension.time, 0.0))
        self.__scenario.storyboard.init.add_init_action(entity_name, init_teleport_action)
        self.__scenario.storyboard.init.add_init_action(entity_name, init_speed_action)

    def add_maneuver(self, entity_name, maneuver_name, trigger_time):
        maneuver = xosc.utils.CatalogReference('ManeuverCatalog', maneuver_name)
        maneuver.add_parameter_assignment('owner', entity_name)
        suffix = '' if entity_name != 'ego' else '-EGO'
        maneuver.add_parameter_assignment('triggerTime', '$MG-TT' + str(self.__maneuver_group_index) + suffix)
        self.add_global_parameter('MG-TT' + str(self.__maneuver_group_index) + suffix, trigger_time, 'double', trigger_time-1, trigger_time+1)
        # add rate parameter
        if maneuver_name.startswith('accelerate') or maneuver_name.startswith('decelerate'):
            maneuver.add_parameter_assignment('rate', '$MG-RT' + str(self.__maneuver_group_index) + suffix)
            rate = 1.0 if maneuver_name.startswith('accelerate') else -1.0
            if maneuver_name.endswith('hard'):
                rate *= 3.0
            self.add_global_parameter('MG-RT' + str(self.__maneuver_group_index) + suffix, rate, 'double', rate-1.0, rate+1.0) # TODO
        # add duration parameter
        maneuver.add_parameter_assignment('duration', '$MG-DU' + str(self.__maneuver_group_index) + suffix)
        if maneuver_name.startswith('merge'):
            self.add_global_parameter('MG-DU' + str(self.__maneuver_group_index) + suffix, 3.0, 'double', 1.0, 5.0) # TODO
        if maneuver_name.startswith('accelerate') or maneuver_name.startswith('decelerate'):
            self.add_global_parameter('MG-DU' + str(self.__maneuver_group_index) + suffix, 1.0, 'double', 0.3, 3.0) # TODO

        mg = xosc.storyboard.ManeuverGroup('MG' + str(self.__maneuver_group_index))
        mg.add_actor(entity_name)
        self.__maneuver_group_index += 1
        # mg.add_maneuver(maneuver)
        mg.maneuvers.append(maneuver)
        self.__scenario.storyboard.stories[0].acts[0].add_maneuver_group(mg)

    def write(self, output_path):
        self.__scenario.write_xml(output_path)

    def add_global_parameter(self, parameter_name, parameter_value, parameter_type='string', min_value=None, max_value=None):
        if parameter_type == 'double':
            ty = xosc.ParameterType.double
        else:
            ty = xosc.ParameterType.string
        if min_value is not None and max_value is not None:
            parameter = ParameterWithRange(parameter_name, ty, parameter_value, min_value, max_value)
        else:
            parameter = xosc.utils.Parameter(parameter_name, ty, parameter_value)
        self.__scenario.parameters.add_parameter(parameter)


# 覆盖scenariogeneration库中的Parameter类, 增加对range的支持
class ParameterWithRange(xosc.utils.Parameter):
    def __init__(self, name, parameter_type, value, min_value, max_value):
        super().__init__(name, parameter_type, value)
        self.min = min_value
        self.max = max_value
    
    def get_attributes(self):
        """ returns the attributes of the Parameter as a dict

        """
        return {'name':self.name,'parameterType':self.parameter_type.get_name(),'value':str(self.value),'min':str(self.min),'max':str(self.max)}
