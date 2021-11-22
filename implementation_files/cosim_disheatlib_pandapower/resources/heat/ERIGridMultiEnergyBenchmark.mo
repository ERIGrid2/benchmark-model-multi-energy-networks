within ;
package ERIGridMultiEnergyBenchmark

  model DHNetworkMassFlowControlled
    "This model implements the thermal system of the multi-energy network benchmark. The heating network is operated by directly controlling the mass flow, always providing enough to satisfy the demand of the consumers."
    DisHeatLib.Boundary.SoilTemperature soilTemperature(
      inputType=DisHeatLib.Boundary.BaseClasses.InputTypeSoilTemp.Constant,
      T_const(displayUnit="degC") = 281.15,
      T_mean=283.15,
      T_amp(displayUnit="degC") = 10,
      t_min=0) annotation (Placement(transformation(extent={{30,120},{50,100}})));
    DisHeatLib.Pipes.DualPipe pipe_l1(
      show_T=true,
      redeclare package Medium = IBPSA.Media.Water,
      redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
      L=500,
      nPorts1=1,
      nPorts2=1)
      annotation (Placement(transformation(extent={{-140,-20},{-120,0}})));
    DisHeatLib.Pipes.DualPipe pipe_l2(
      show_T=true,
      redeclare package Medium = IBPSA.Media.Water,
      redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
      L=500,
      nPorts1=1,
      nPorts2=1)
      annotation (Placement(transformation(extent={{-50,-20},{-30,0}})));
    DisHeatLib.Pipes.DualPipe pipe_l3(
      show_T=true,
      redeclare package Medium = IBPSA.Media.Water,
      redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
      L=10,
      nPorts1=1,
      nPorts2=1)
      annotation (Placement(transformation(extent={{-10,-10},{10,10}},
          rotation=90,
          origin={0,30})));
    DisHeatLib.Pipes.DualPipe pipe_l4(
      show_T=true,
      redeclare package Medium = IBPSA.Media.Water,
      redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
      L=500,
      nPorts2=1,
      nPorts1=1)
      annotation (Placement(transformation(extent={{30,-20},{50,0}})));
    DisHeatLib.Pipes.DualPipe pipe_l5(
      show_T=true,
      redeclare package Medium = IBPSA.Media.Water,
      redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
      L=500,
      nPorts1=1,
      nPorts2=1)
      annotation (Placement(transformation(extent={{-10,-10},{10,10}},
          rotation=90,
          origin={80,30})));
    DisHeatLib.Pipes.DualPipe pipe_l6(
      show_T=true,
      redeclare package Medium = IBPSA.Media.Water,
      redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
      L=10,
      nPorts1=1,
      nPorts2=1)
      annotation (Placement(transformation(extent={{110,-20},{130,0}})));
    IBPSA.Fluid.FixedResistances.Junction junction_n4r(
      redeclare package Medium = IBPSA.Media.Water,
      m_flow_nominal={10,-20,10},
      dp_nominal={10,-10,10})
      annotation (Placement(transformation(extent={{20,-6},{0,-26}})));
    IBPSA.Fluid.FixedResistances.Junction junction_n4s(
      redeclare package Medium = IBPSA.Media.Water,
      m_flow_nominal={20,-10,-10},
      dp_nominal={10,-10,-10})
      annotation (Placement(transformation(extent={{-20,6},{0,-14}})));
    IBPSA.Fluid.FixedResistances.Junction junction_n6r(
      redeclare package Medium = IBPSA.Media.Water,
      m_flow_nominal={10,-20,10},
      dp_nominal={10,-10,10})
      annotation (Placement(transformation(extent={{100,-6},{80,-26}})));
    IBPSA.Fluid.FixedResistances.Junction junction_n6s(
      redeclare package Medium = IBPSA.Media.Water,
      m_flow_nominal={20,-10,-10},
      dp_nominal={10,-10,-10})
      annotation (Placement(transformation(extent={{60,6},{80,-14}})));
    IBPSA.Fluid.Actuators.Valves.TwoWayLinear valve_grid_v1(
      redeclare package Medium = IBPSA.Media.Water,
      m_flow_nominal=20,
      CvData=IBPSA.Fluid.Types.CvTypes.OpPoint,
      dpValve_nominal=10)
      annotation (Placement(transformation(extent={{-110,6},{-90,-14}})));
    Components.Consumer consumer1(fileName=fileNameConsumer1)
      annotation (Placement(transformation(extent={{10,60},{-10,80}})));
    Components.Consumer consumer2(fileName=fileNameConsumer2)
      annotation (Placement(transformation(extent={{90,60},{70,80}})));
    Components.Bypass bypass(
      show_T=true,
      m_flow_min=2.0,
      dpValve_nominal=1000000,
      T_min=333.15)
      annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=-90,
          origin={160,-10})));
    Components.PowerToHeat powerToHeat(show_T=true,
      nTankSenseTempHigh=nTankSenseTempHigh,
      nTankSenseTempLow=nTankSenseTempLow)
      annotation (Placement(transformation(extent={{-80,-20},{-60,0}})));
    Modelica.Blocks.Interfaces.RealInput valve_grid_v1_setpoint annotation (
        Placement(transformation(
          extent={{20,-20},{-20,20}},
          rotation=-90,
          origin={-170,-110}), iconTransformation(
          extent={{20,-20},{-20,20}},
          rotation=-90,
          origin={-170,-108})));
    Modelica.Blocks.Interfaces.RealInput mdot_condenser_in annotation (Placement(
          transformation(
          extent={{20,-20},{-20,20}},
          rotation=-90,
          origin={-110,-108}), iconTransformation(
          extent={{20,-20},{-20,20}},
          rotation=-90,
          origin={-110,-108})));
    Modelica.Blocks.Interfaces.RealInput mdot_tank_out annotation (Placement(
          transformation(
          extent={{20,-20},{-20,20}},
          rotation=-90,
          origin={-50,-108}), iconTransformation(
          extent={{20,-20},{-20,20}},
          rotation=-90,
          origin={-50,-108})));
    Modelica.Blocks.Interfaces.RealOutput P_el_heatpump annotation (Placement(
          transformation(
          extent={{-10,-11},{10,11}},
          rotation=-90,
          origin={32,-109}), iconTransformation(
          extent={{-10,-11},{10,11}},
          rotation=-90,
          origin={20,-110})));
    Modelica.Blocks.Interfaces.RealOutput T_tank_low annotation (Placement(
          transformation(
          extent={{-10,-11},{10,11}},
          rotation=-90,
          origin={90,-109}), iconTransformation(
          extent={{-10,-11},{10,11}},
          rotation=-90,
          origin={80,-110})));
    Modelica.Blocks.Interfaces.RealOutput T_tank_high annotation (Placement(
          transformation(
          extent={{-10,-11},{10,11}},
          rotation=-90,
          origin={150,-109}), iconTransformation(
          extent={{-10,-11},{10,11}},
          rotation=-90,
          origin={140,-110})));
    Modelica.Blocks.Sources.RealExpression m_flow_request(y=consumer1.m_flow_demand
           + consumer2.m_flow_demand + bypass.m_flow_bypass - mdot_tank_out)
      annotation (Placement(transformation(extent={{-140,30},{-160,50}})));
    Components.ExternalGridMassFlowControlled externalGrid(show_T=true)
      annotation (Placement(transformation(extent={{-180,0},{-160,20}})));

    parameter String fileNameConsumer1="modelica://ERIGridMultiEnergyBenchmark/data/simple_profile_consumer1_1day.txt" "File where matrix is stored";
    parameter String fileNameConsumer2="modelica://ERIGridMultiEnergyBenchmark/data/simple_profile_consumer2_1day.txt" "File where matrix is stored";

    parameter Integer nTankSenseTempHigh=1 "Position of upper tank temperature sensor (number of tank segment)";
    parameter Integer nTankSenseTempLow=10 "Position of lower tank temperature sensor (number of tank segment)";

  equation
    connect(soilTemperature.port,pipe_l2. port_ht)
      annotation (Line(points={{40,100},{40,90},{-40,90},{-40,0}},color={191,0,0}));
    connect(soilTemperature.port,pipe_l4. port_ht) annotation (Line(points={{40,100},
            {40,0}},color={191,0,0}));
    connect(junction_n4s.port_1, pipe_l2.ports_b1[1])
      annotation (Line(points={{-20,-4},{-30,-4}},color={0,127,255}));
    connect(junction_n4s.port_2, pipe_l4.port_a1)
      annotation (Line(points={{0,-4},{30,-4}},color={0,127,255}));
    connect(pipe_l4.ports_b2[1], junction_n4r.port_1)
      annotation (Line(points={{30,-16},{20,-16}}, color={0,127,255}));
    connect(junction_n4s.port_3, pipe_l3.port_a1) annotation (Line(points={{-10,6},
            {-10,12},{-6,12},{-6,20}},color={0,127,255}));
    connect(pipe_l3.ports_b1[1], consumer1.port_b) annotation (Line(points={{-6,40},
            {-6,50},{-20,50},{-20,70},{-10,70}},color={0,127,255}));
    connect(consumer1.port_a, pipe_l3.port_a2) annotation (Line(points={{10,70},
            {20,70},{20,50},{6,50},{6,40}}, color={0,127,255}));
    connect(junction_n6s.port_3, pipe_l5.port_a1) annotation (Line(points={{70,6},{
            70,12},{74,12},{74,20}},color={0,127,255}));
    connect(pipe_l4.ports_b1[1], junction_n6s.port_1)
      annotation (Line(points={{50,-4},{60,-4}},color={0,127,255}));
    connect(pipe_l5.ports_b1[1], consumer2.port_b) annotation (Line(points={{74,40},
            {74,50},{60,50},{60,70},{70,70}},color={0,127,255}));
    connect(pipe_l5.port_a2, consumer2.port_a) annotation (Line(points={{86,40},
            {86,50},{100,50},{100,70},{90,70}},color={0,127,255}));
    connect(junction_n6s.port_2, pipe_l6.port_a1)
      annotation (Line(points={{80,-4},{110,-4}},color={0,127,255}));
    connect(pipe_l5.port_ht, soilTemperature.port)
      annotation (Line(points={{70,30},{40,30},{40,100}},color={191,0,0}));
    connect(pipe_l3.port_ht, soilTemperature.port) annotation (Line(points={{-10,30},
            {-40,30},{-40,90},{40,90},{40,100}},color={191,0,0}));
    connect(pipe_l6.port_ht, soilTemperature.port) annotation (Line(points={{120,0},
            {120,90},{40,90},{40,100}},color={191,0,0}));
    connect(pipe_l6.ports_b1[1], bypass.port_a) annotation (Line(points={{130,-4},
            {140,-4},{140,10},{160,10},{160,0}},color={0,127,255}));
    connect(pipe_l6.port_a2, bypass.port_b) annotation (Line(points={{130,-16},
            {140,-16},{140,-30},{160,-30},{160,-20}},color={0,127,255}));
    connect(pipe_l1.ports_b1[1], valve_grid_v1.port_a)
      annotation (Line(points={{-120,-4},{-110,-4}},color={0,127,255}));
    connect(powerToHeat.port_a1, valve_grid_v1.port_b)
      annotation (Line(points={{-80,-4},{-90,-4}},color={0,127,255}));
    connect(powerToHeat.port_b1, pipe_l2.port_a1)
      annotation (Line(points={{-60,-4},{-50,-4}},color={0,127,255}));
    connect(powerToHeat.port_ht, soilTemperature.port) annotation (Line(points={{-70,0},
            {-70,30},{-40,30},{-40,90},{40,90},{40,100}},color={191,0,0}));
    connect(pipe_l1.port_ht, soilTemperature.port) annotation (Line(points={{-130,0},
            {-130,30},{-40,30},{-40,90},{40,90},{40,100}},color={191,0,0}));
    connect(valve_grid_v1_setpoint, valve_grid_v1.y)
      annotation (Line(points={{-170,-110},{-170,-56},{-100,-56},{-100,-16}},color={0,0,127}));
    connect(powerToHeat.mdot_tank_out, mdot_tank_out) annotation (Line(points={{-75,-21},
            {-75,-68},{-50,-68},{-50,-108}},color={0,0,127}));
    connect(powerToHeat.P_el_heatpump, P_el_heatpump) annotation (Line(points={{-67,
            -20.5},{-67,-64},{32,-64},{32,-109}},color={0,0,127}));
    connect(powerToHeat.T_tank_low, T_tank_low) annotation (Line(points={{-64,-20.5},
            {-64,-60},{90,-60},{90,-109}},color={0,0,127}));
    connect(powerToHeat.T_tank_high, T_tank_high) annotation (Line(points={{-61,
            -20.5},{-61,-56},{150,-56},{150,-109}},color={0,0,127}));
    connect(powerToHeat.port_a2, pipe_l2.ports_b2[1])
      annotation (Line(points={{-60,-16},{-50,-16}},color={0,127,255}));
    connect(pipe_l2.port_a2, junction_n4r.port_2)
      annotation (Line(points={{-30,-16},{0,-16}},color={0,127,255}));
    connect(pipe_l4.port_a2, junction_n6r.port_2)
      annotation (Line(points={{50,-16},{80,-16}},color={0,127,255}));
    connect(junction_n6r.port_1, pipe_l6.ports_b2[1])
      annotation (Line(points={{100,-16},{110,-16}},color={0,127,255}));
    connect(pipe_l1.port_a2, powerToHeat.port_b2)
      annotation (Line(points={{-120,-16},{-80,-16}},color={0,127,255}));
    connect(pipe_l3.ports_b2[1], junction_n4r.port_3) annotation (Line(points={
            {6,20},{6,12},{10,12},{10,-6}}, color={0,127,255}));
    connect(pipe_l5.ports_b2[1], junction_n6r.port_3) annotation (Line(points={
            {86,20},{86,12},{90,12},{90,-6}}, color={0,127,255}));
    connect(mdot_condenser_in, powerToHeat.mdot_condenser_in) annotation (Line(
          points={{-110,-108},{-110,-60},{-79,-60},{-79,-21}}, color={0,0,127}));
    connect(m_flow_request.y, externalGrid.m_flow_request) annotation (Line(
          points={{-161,40},{-170,40},{-170,22}}, color={0,0,127}));
    connect(pipe_l1.port_a1, externalGrid.port_b) annotation (Line(points={{
            -140,-4},{-150,-4},{-150,10},{-160,10}}, color={0,127,255}));
    connect(pipe_l1.ports_b2[1], externalGrid.port_a) annotation (Line(points={
            {-140,-16},{-190,-16},{-190,10},{-180,10}}, color={0,127,255}));
    annotation (
      Icon(
        coordinateSystem(preserveAspectRatio=false, extent={{-200,-100},{180,140}}),
        graphics={
          Text(
            extent={{-60,200},{60,140}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            lineThickness=1,
            fillColor={0,0,173},
            fillPattern=FillPattern.Solid,
            textString="%name"),
          Rectangle(
            extent={{-200,140},{180,-100}},
            lineColor={0,0,0},
            fillColor={227,221,16},
            fillPattern=FillPattern.Solid,
            radius=20),
          Text(
            extent={{-200,140},{180,-100}},
            lineColor={0,0,0},
            textString="m"),
          Ellipse(
            extent={{-22,100},{2,76}},
            pattern=LinePattern.None,
            lineColor={0,0,0},
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid)}),
        Diagram(coordinateSystem(preserveAspectRatio=
          false, extent={{-200,-100},{180,140}})),
      experiment(StopTime=86400, __Dymola_Algorithm="Dassl"),
      Documentation(info="<html>
    <p>This model implements the thermal system of the multi-energy network benchmark. The heating network is operated by directly controlling the mass flow, always providing enough to satisfy the demand of the consumers.</p>
    </html>"));
  end DHNetworkMassFlowControlled;

  model DHNetworkPressureControlled
    "This model implements the thermal system of the multi-energy network benchmark. The heating network is operated by controlling the pressure, keeping the pressure drop at the consumers above a certain threshold."
    DisHeatLib.Boundary.SoilTemperature soilTemperature(
      inputType=DisHeatLib.Boundary.BaseClasses.InputTypeSoilTemp.Constant,
      T_const(displayUnit="degC") = 283.15,
      T_mean=283.15,
      T_amp(displayUnit="degC") = 10,
      t_min=0) annotation (Placement(transformation(extent={{30,120},{50,100}})));
    DisHeatLib.Pipes.DualPipe pipe_l1(
      show_T=true,
      redeclare package Medium = IBPSA.Media.Water,
      redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
      L=500,
      nPorts1=1,
      nPorts2=1)
      annotation (Placement(transformation(extent={{-140,-20},{-120,0}})));
    DisHeatLib.Pipes.DualPipe pipe_l2(
      show_T=true,
      redeclare package Medium = IBPSA.Media.Water,
      redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
      L=500,
      nPorts1=1,
      nPorts2=1)
      annotation (Placement(transformation(extent={{-50,-20},{-30,0}})));
    DisHeatLib.Pipes.DualPipe pipe_l3(
      show_T=true,
      redeclare package Medium = IBPSA.Media.Water,
      redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
      L=10,
      nPorts1=1,
      nPorts2=1)
      annotation (Placement(transformation(extent={{-10,-10},{10,10}},
          rotation=90,
          origin={0,30})));
    DisHeatLib.Pipes.DualPipe pipe_l4(
      show_T=true,
      redeclare package Medium = IBPSA.Media.Water,
      redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
      L=500,
      nPorts2=1,
      nPorts1=1)
      annotation (Placement(transformation(extent={{30,-20},{50,0}})));
    DisHeatLib.Pipes.DualPipe pipe_l5(
      show_T=true,
      redeclare package Medium = IBPSA.Media.Water,
      redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
      L=500,
      nPorts1=1,
      nPorts2=1)
      annotation (Placement(transformation(extent={{-10,-10},{10,10}},
          rotation=90,
          origin={80,30})));
    DisHeatLib.Pipes.DualPipe pipe_l6(
      show_T=true,
      redeclare package Medium = IBPSA.Media.Water,
      redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
      L=10,
      nPorts1=1,
      nPorts2=1)
      annotation (Placement(transformation(extent={{110,-20},{130,0}})));
    IBPSA.Fluid.FixedResistances.Junction junction_n4r(
      redeclare package Medium = IBPSA.Media.Water,
      m_flow_nominal={10,-20,10},
      dp_nominal={10,-10,10})
      annotation (Placement(transformation(extent={{20,-6},{0,-26}})));
    IBPSA.Fluid.FixedResistances.Junction junction_n4s(
      redeclare package Medium = IBPSA.Media.Water,
      m_flow_nominal={20,-10,-10},
      dp_nominal={10,-10,-10})
      annotation (Placement(transformation(extent={{-20,6},{0,-14}})));
    IBPSA.Fluid.FixedResistances.Junction junction_n6s(
      redeclare package Medium = IBPSA.Media.Water,
      m_flow_nominal={20,-10,-10},
      dp_nominal={10,-10,-10})
      annotation (Placement(transformation(extent={{60,6},{80,-14}})));
    IBPSA.Fluid.FixedResistances.Junction junction_n6r(
      redeclare package Medium = IBPSA.Media.Water,
      m_flow_nominal={10,-20,10},
      dp_nominal={10,-10,10})
      annotation (Placement(transformation(extent={{100,-6},{80,-26}})));
    IBPSA.Fluid.Actuators.Valves.TwoWayLinear valve_grid_v1(
      redeclare package Medium = IBPSA.Media.Water,
      m_flow_nominal=20,
      CvData=IBPSA.Fluid.Types.CvTypes.OpPoint,
      dpValve_nominal=10)
      annotation (Placement(transformation(extent={{-110,6},{-90,-14}})));
    Components.PowerToHeat powerToHeat(nTankSenseTempHigh=nTankSenseTempHigh,
        nTankSenseTempLow=nTankSenseTempLow)
      annotation (Placement(transformation(extent={{-80,-20},{-60,0}})));
    Components.ConsumerSubstation consumer1(fileName=
          fileNameConsumer1)
      annotation (Placement(transformation(extent={{10,60},{-10,80}})));
    Components.ConsumerSubstation consumer2(fileName=
          fileNameConsumer2)
      annotation (Placement(transformation(extent={{90,60},{70,80}})));
    Components.Bypass bypass(m_flow_nominal=2, dpValve_nominal=100000)
                                annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=-90,
          origin={160,-10})));
    Modelica.Blocks.Sources.RealExpression dp_measure_min(y=min([consumer1.dp,
          consumer2.dp]))
      annotation (Placement(transformation(extent={{-140,30},{-160,50}})));
    Modelica.Blocks.Interfaces.RealInput valve_grid_v1_setpoint annotation (
        Placement(transformation(
          extent={{20,-20},{-20,20}},
          rotation=-90,
          origin={-170,-110}), iconTransformation(
          extent={{20,-20},{-20,20}},
          rotation=-90,
          origin={-170,-108})));
    Modelica.Blocks.Interfaces.RealInput mdot_condenser_in annotation (Placement(
          transformation(
          extent={{20,-20},{-20,20}},
          rotation=-90,
          origin={-110,-108}), iconTransformation(
          extent={{20,-20},{-20,20}},
          rotation=-90,
          origin={-110,-108})));
    Modelica.Blocks.Interfaces.RealInput mdot_tank_out annotation (Placement(
          transformation(
          extent={{20,-20},{-20,20}},
          rotation=-90,
          origin={-50,-108}), iconTransformation(
          extent={{20,-20},{-20,20}},
          rotation=-90,
          origin={-50,-108})));
    Modelica.Blocks.Interfaces.RealOutput P_el_heatpump annotation (Placement(
          transformation(
          extent={{-10,-11},{10,11}},
          rotation=-90,
          origin={32,-109}), iconTransformation(
          extent={{-10,-11},{10,11}},
          rotation=-90,
          origin={20,-110})));
    Modelica.Blocks.Interfaces.RealOutput T_tank_low annotation (Placement(
          transformation(
          extent={{-10,-11},{10,11}},
          rotation=-90,
          origin={90,-109}), iconTransformation(
          extent={{-10,-11},{10,11}},
          rotation=-90,
          origin={80,-110})));
    Modelica.Blocks.Interfaces.RealOutput T_tank_high annotation (Placement(
          transformation(
          extent={{-10,-11},{10,11}},
          rotation=-90,
          origin={150,-109}), iconTransformation(
          extent={{-10,-11},{10,11}},
          rotation=-90,
          origin={140,-110})));
    Components.ExternalGridPressureControlled externalGrid(show_T=true)
      annotation (Placement(transformation(extent={{-180,0},{-160,20}})));

    parameter String fileNameConsumer1="modelica://ERIGridMultiEnergyBenchmark/data/simple_profile_consumer1_1day.txt" "File where matrix is stored";
    parameter String fileNameConsumer2="modelica://ERIGridMultiEnergyBenchmark/data/simple_profile_consumer2_1day.txt" "File where matrix is stored";

    parameter Integer nTankSenseTempHigh=2 "Position of upper tank temperature sensor (number of tank segment)";
    parameter Integer nTankSenseTempLow=9 "Position of lower tank temperature sensor (number of tank segment)";

  equation
    connect(soilTemperature.port,pipe_l2. port_ht)
      annotation (Line(points={{40,100},{40,90},{-40,90},{-40,0}},color={191,0,0}));
    connect(soilTemperature.port,pipe_l4. port_ht) annotation (Line(points={{40,100},
            {40,0}},color={191,0,0}));
    connect(junction_n4s.port_1, pipe_l2.ports_b1[1])
      annotation (Line(points={{-20,-4},{-30,-4}},color={0,127,255}));
    connect(junction_n4s.port_2, pipe_l4.port_a1)
      annotation (Line(points={{0,-4},{30,-4}},color={0,127,255}));
    connect(pipe_l4.ports_b2[1], junction_n4r.port_1)
      annotation (Line(points={{30,-16},{20,-16}}, color={0,127,255}));
    connect(junction_n4s.port_3, pipe_l3.port_a1) annotation (Line(points={{-10,6},
            {-10,12},{-6,12},{-6,20}},color={0,127,255}));
    connect(pipe_l3.ports_b1[1], consumer1.port_b) annotation (Line(points={{-6,40},
            {-6,50},{-20,50},{-20,70},{-10,70}},color={0,127,255}));
    connect(consumer1.port_a, pipe_l3.port_a2) annotation (Line(points={{10,70},
            {20,70},{20,50},{6,50},{6,40}}, color={0,127,255}));
    connect(junction_n6s.port_3, pipe_l5.port_a1) annotation (Line(points={{70,6},{
            70,12},{74,12},{74,20}},color={0,127,255}));
    connect(pipe_l4.ports_b1[1], junction_n6s.port_1)
      annotation (Line(points={{50,-4},{60,-4}},color={0,127,255}));
    connect(pipe_l5.ports_b1[1], consumer2.port_b) annotation (Line(points={{74,40},
            {74,50},{60,50},{60,70},{70,70}},color={0,127,255}));
    connect(pipe_l5.port_a2, consumer2.port_a) annotation (Line(points={{86,40},
            {86,50},{100,50},{100,70},{90,70}},color={0,127,255}));
    connect(junction_n6s.port_2, pipe_l6.port_a1)
      annotation (Line(points={{80,-4},{110,-4}},color={0,127,255}));
    connect(pipe_l5.port_ht, soilTemperature.port)
      annotation (Line(points={{70,30},{40,30},{40,100}},color={191,0,0}));
    connect(pipe_l3.port_ht, soilTemperature.port) annotation (Line(points={{-10,30},
            {-40,30},{-40,90},{40,90},{40,100}},color={191,0,0}));
    connect(pipe_l6.port_ht, soilTemperature.port) annotation (Line(points={{120,0},
            {120,90},{40,90},{40,100}},color={191,0,0}));
    connect(pipe_l6.ports_b1[1], bypass.port_a) annotation (Line(points={{130,-4},
            {140,-4},{140,10},{160,10},{160,0}},color={0,127,255}));
    connect(pipe_l6.port_a2, bypass.port_b) annotation (Line(points={{130,-16},
            {140,-16},{140,-30},{160,-30},{160,-20}}, color={0,127,255}));
    connect(pipe_l1.ports_b1[1], valve_grid_v1.port_a)
      annotation (Line(points={{-120,-4},{-110,-4}},color={0,127,255}));
    connect(powerToHeat.port_a1, valve_grid_v1.port_b)
      annotation (Line(points={{-80,-4},{-90,-4}},color={0,127,255}));
    connect(powerToHeat.port_b1, pipe_l2.port_a1)
      annotation (Line(points={{-60,-4},{-50,-4}}, color={0,127,255}));
    connect(powerToHeat.port_ht, soilTemperature.port) annotation (Line(points={{-70,0},
            {-70,30},{-40,30},{-40,90},{40,90},{40,100}},color={191,0,0}));
    connect(pipe_l1.port_ht, soilTemperature.port) annotation (Line(points={{-130,0},
            {-130,30},{-40,30},{-40,90},{40,90},{40,100}},color={191,0,0}));
    connect(valve_grid_v1_setpoint, valve_grid_v1.y)
      annotation (Line(points={{-170,-110},{-170,-56},{-100,-56},{-100,-16}},color={0,0,127}));
    connect(powerToHeat.mdot_tank_out, mdot_tank_out) annotation (Line(points={{-75,-21},
            {-75,-68},{-50,-68},{-50,-108}},      color={0,0,127}));
    connect(powerToHeat.P_el_heatpump, P_el_heatpump) annotation (Line(points={{-67,
            -20.5},{-67,-64},{32,-64},{32,-109}}, color={0,0,127}));
    connect(powerToHeat.T_tank_low, T_tank_low) annotation (Line(points={{-64,-20.5},
            {-64,-60},{90,-60},{90,-109}},   color={0,0,127}));
    connect(powerToHeat.T_tank_high, T_tank_high) annotation (Line(points={{-61,
            -20.5},{-61,-56},{150,-56},{150,-109}},
                                             color={0,0,127}));
    connect(powerToHeat.port_a2, pipe_l2.ports_b2[1])
      annotation (Line(points={{-60,-16},{-50,-16}}, color={0,127,255}));
    connect(pipe_l2.port_a2, junction_n4r.port_2)
      annotation (Line(points={{-30,-16},{0,-16}}, color={0,127,255}));
    connect(pipe_l4.port_a2, junction_n6r.port_2)
      annotation (Line(points={{50,-16},{80,-16}},  color={0,127,255}));
    connect(junction_n6r.port_1, pipe_l6.ports_b2[1])
      annotation (Line(points={{100,-16},{110,-16}}, color={0,127,255}));
    connect(pipe_l1.port_a2, powerToHeat.port_b2)
      annotation (Line(points={{-120,-16},{-80,-16}},  color={0,127,255}));
    connect(pipe_l3.ports_b2[1], junction_n4r.port_3) annotation (Line(points={
            {6,20},{6,12},{10,12},{10,-6}}, color={0,127,255}));
    connect(pipe_l5.ports_b2[1], junction_n6r.port_3) annotation (Line(points={
            {86,20},{86,12},{90,12},{90,-6}}, color={0,127,255}));
    connect(mdot_condenser_in, powerToHeat.mdot_condenser_in) annotation (Line(
          points={{-110,-108},{-110,-60},{-79,-60},{-79,-21}}, color={0,0,127}));
    connect(externalGrid.dp_measure, dp_measure_min.y) annotation (Line(points=
            {{-170,22},{-170,40},{-161,40}}, color={0,0,127}));
    connect(externalGrid.port_b, pipe_l1.port_a1) annotation (Line(points={{
            -160,10},{-150,10},{-150,-4},{-140,-4}}, color={0,127,255}));
    connect(pipe_l1.ports_b2[1], externalGrid.port_a) annotation (Line(points={
            {-140,-16},{-190,-16},{-190,10},{-180,10}}, color={0,127,255}));
    annotation (
      Icon(
        coordinateSystem(preserveAspectRatio=false, extent={{-200,-100},{180,140}}),
        graphics={
          Text(
            extent={{-60,200},{60,140}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            lineThickness=1,
            fillColor={0,0,173},
            fillPattern=FillPattern.Solid,
            textString="%name"),         Rectangle(
            extent={{-200,140},{180,-100}},
            lineColor={0,0,0},
            fillColor={227,221,16},
            fillPattern=FillPattern.Solid,
            radius=20),
          Text(
            extent={{-200,140},{180,-100}},
            lineColor={0,0,0},
            textString="P")}),
      Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-200,-100},{180,140}})),
      experiment(StopTime=86400, __Dymola_Algorithm="Dassl"),
      Documentation(info="<html>
    <p>This model implements the thermal system of the multi-energy network benchmark. The heating network is operated by controlling the pressure, keeping the pressure drop at the consumers above a certain threshold.</p>
    </html>"));
  end DHNetworkPressureControlled;

  package Components
    "This sub-package contains components used for modelling the thermal system of the multi-energy network benchmark"
    model Bypass
      "Hydraulic bypass of the thermal network."
      extends IBPSA.Fluid.Interfaces.PartialTwoPortInterface(
        m_flow_nominal = 10,
        redeclare package Medium = IBPSA.Media.Water);

      IBPSA.Fluid.Actuators.Valves.TwoWayLinear val(
        redeclare package Medium = IBPSA.Media.Water,
        m_flow_nominal=m_flow_nominal,
        show_T=true,
        dpValve_nominal=dpValve_nominal)
        annotation (Placement(transformation(extent={{-60,-50},{-40,-30}})));
      DisHeatLib.Controls.bypass_control bypass_control(T_min=T_min)
        annotation (Placement(transformation(extent={{20,-30},{0,-10}})));
      IBPSA.Fluid.Sensors.Temperature senTem(redeclare package Medium =
            IBPSA.Media.Water)
        annotation (Placement(transformation(extent={{60,-30},{40,-10}})));
      Modelica.Blocks.Math.Max max
        annotation (Placement(transformation(extent={{-20,-10},{-40,10}})));
      Modelica.Blocks.Math.Gain gain(k=m_flow_nominal) annotation (Placement(
            transformation(
            extent={{-10,-10},{10,10}},
            rotation=90,
            origin={0,70})));
      Modelica.Blocks.Sources.RealExpression u_flow_min(y=m_flow_min/m_flow_nominal)
        annotation (Placement(transformation(extent={{20,10},{0,30}})));
      Modelica.Blocks.Interfaces.RealOutput m_flow_bypass annotation (Placement(
            transformation(
            extent={{-10,-10},{10,10}},
            rotation=90,
            origin={0,110})));

      parameter Modelica.SIunits.MassFlowRate m_flow_min=0;

      parameter Modelica.SIunits.PressureDifference dpValve_nominal
        "Nominal pressure drop of fully open valve, used if CvData=IBPSA.Fluid.Types.CvTypes.OpPoint";

      parameter Modelica.SIunits.Temperature T_min=65.0 + 273.15
        "Minimum temperature for bypass activation";

    equation
      connect(port_a, val.port_a) annotation (Line(points={{-100,0},{-80,0},{-80,-40},
              {-60,-40}},          color={0,127,255}));
      connect(bypass_control.T_measurement, senTem.T)
        annotation (Line(points={{22,-20},{43,-20}}, color={0,0,127}));
      connect(senTem.port, val.port_b)
        annotation (Line(points={{50,-30},{50,-40},{-40,-40}},color={0,127,255}));
      connect(port_b, val.port_b)
        annotation (Line(points={{100,0},{80,0},{80,-40},{-40,-40}},color={0,127,255}));
      connect(bypass_control.y,max. u2) annotation (Line(points={{-1,-20},{-10,-20},
              {-10,-6},{-18,-6}}, color={0,0,127}));
      connect(val.y,max. y)
        annotation (Line(points={{-50,-28},{-50,0},{-41,0}}, color={0,0,127}));
      connect(max.u1, u_flow_min.y) annotation (Line(points={{-18,6},{-10,6},{-10,20},
              {-1,20}}, color={0,0,127}));
      connect(m_flow_bypass, gain.y)
        annotation (Line(points={{0,110},{0,81}}, color={0,0,127}));
      connect(gain.u,max. y) annotation (Line(points={{0,58},{0,40},{-50,40},{-50,0},
              {-41,0}}, color={0,0,127}));
      annotation (
        Icon(
          coordinateSystem(preserveAspectRatio=false),
          graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={227,221,16},
              fillPattern=FillPattern.Solid,
              radius=15),
            Ellipse(
              extent={{-88,88},{88,-88}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Bitmap(
              extent={{-70,-56},{70,64}}, fileName=
                  "modelica://ERIGridMultiEnergyBenchmark/images/bypass.svg")}),
        Diagram(coordinateSystem(preserveAspectRatio=false)));
    end Bypass;

    model Consumer
      "Consumer in the thermal network, modelled as a heat exchanger."
      extends IBPSA.Fluid.Interfaces.PartialTwoPortInterface(
        m_flow_nominal = 4,
        redeclare package Medium = IBPSA.Media.Water);

      DisHeatLib.Demand.Demand demand(
        redeclare package Medium = IBPSA.Media.Water,
        allowFlowReversal=true,
        m_flow_nominal=m_flow_nominal,
        show_T=true,
        dp_nominal(displayUnit="bar") = 100000,
        Q_flow_nominal(displayUnit="kW") = Q_flow_nominal,
        TemSup_nominal=348.15,
        TemRet_nominal=313.15,
        heatLoad=DisHeatLib.Demand.BaseClasses.InputTypeDemand.FileQ,
        scaling=1000,
        tableName=tableName,
        fileName=fileName,
        redeclare DisHeatLib.Demand.BaseDemands.Radiator demandType)
        annotation (Placement(transformation(extent={{-10,-10},{-30,10}})));
      IBPSA.Fluid.Sensors.MassFlowRate senMasFlo(redeclare package Medium =
            IBPSA.Media.Water) annotation (Placement(transformation(
            extent={{10,-10},{-10,10}},
            rotation=0,
            origin={20,0})));
      Modelica.Blocks.Interfaces.RealOutput m_flow_demand annotation (Placement(
            transformation(
            extent={{10,-10},{-10,10}},
            rotation=-90,
            origin={0,110})));

      parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal(displayUnit="kW") = 750000;
      // parameter Modelica.SIunits.MassFlowRate m_flow_nominal = 4;
      parameter String fileName="C:/Development/erigrid2/JRA-1.1-multi-energy/disheatlib_standalone/resources/heat/heat_demand_load_profile_test.txt"
        "File where matrix is stored"
            annotation(Dialog(loadSelector(filter="Text files(*.txt);;CSV files (*.csv)",caption="Open data file")));
      parameter String tableName="HeatDemand"
        "Table name on file or in function usertab (see docu)";

    equation
      connect(senMasFlo.m_flow, m_flow_demand) annotation (Line(points={{20,11},
              {20,88},{0,88},{0,110}}, color={0,0,127}));
      connect(demand.port_a, senMasFlo.port_b)
        annotation (Line(points={{-10,0},{10,0}},  color={0,127,255}));
      connect(demand.port_b, port_a)
        annotation (Line(points={{-30,0},{-100,0}}, color={0,127,255}));
      connect(senMasFlo.port_a, port_b)
        annotation (Line(points={{30,0},{100,0}}, color={0,127,255}));
      annotation (
        Icon(
          coordinateSystem(preserveAspectRatio=false),
          graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={227,221,16},
              fillPattern=FillPattern.Solid,
              radius=15),
            Polygon(
              points={{-132,92},{-132,92}},
              lineColor={0,0,0},
              lineThickness=0.5,
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Ellipse(
              extent={{-88,88},{88,-88}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Bitmap(extent={{-50,-54},{50,54}}, fileName=
                  "modelica://ERIGridMultiEnergyBenchmark/images/heat-exchanger.svg")}),
        Diagram(coordinateSystem(preserveAspectRatio=false)));
    end Consumer;

    model ConsumerSubstation
      "Consumer in the thermal network, separated from the supply line via substation."

      DisHeatLib.Demand.Demand demand(
        redeclare package Medium = IBPSA.Media.Water,
        allowFlowReversal=true,
        m_flow_nominal=indirectStation.m2_flow_nominal,
        show_T=true,
        from_dp=true,
        dp_nominal(displayUnit="bar") = 100000,
        Q_flow_nominal(displayUnit="kW") = indirectStation.Q2_flow_nominal,
        TemSup_nominal=348.15,
        TemRet_nominal=308.15,
        heatLoad=DisHeatLib.Demand.BaseClasses.InputTypeDemand.FileQ,
        scaling=1000,
        tableName=tableName,
        fileName=fileName,
        redeclare DisHeatLib.Demand.BaseDemands.Radiator demandType)
        annotation (Placement(transformation(extent={{10,-70},{-10,-50}})));
      IBPSA.Fluid.Sensors.RelativePressure senRelPre(redeclare package Medium =
            IBPSA.Media.Water)
        annotation (Placement(transformation(extent={{10,30},{-10,10}})));
      DisHeatLib.Substations.BaseStations.IndirectStation indirectStation(
        m1_flow_nominal=m_flow_nominal,
        m2_flow_nominal=m_flow_nominal,
        show_T=true,
        redeclare package Medium = IBPSA.Media.Water,
        from_dp=true,
        Q1_flow_nominal(displayUnit="kW") = 750000,
        TemSup1_nominal=348.15,
        TemRet1_nominal=308.15,
        dp1_nominal(displayUnit="bar") = 100000,
        TemSup2_nominal=348.15,
        TemRet2_nominal=308.15,
        OutsideDependent=false,
        Ti=60) annotation (Placement(transformation(extent={{10,-36},{-10,-16}})));
      extends IBPSA.Fluid.Interfaces.PartialTwoPort(
        redeclare package Medium = IBPSA.Media.Water);

      parameter Modelica.SIunits.MassFlowRate m_flow_nominal = 5;
      parameter String fileName="C:/Development/erigrid2/JRA-1.1-multi-energy/disheatlib_standalone/resources/heat/heat_demand_load_profile_test.txt"
        "File where matrix is stored"
            annotation(Dialog(loadSelector(filter="Text files(*.txt);;CSV files (*.csv)",caption="Open data file")));

      parameter String tableName="HeatDemand"
        "Table name on file or in function usertab (see docu)";
      Modelica.Blocks.Interfaces.RealOutput dp annotation (Placement(
            transformation(
            extent={{-10,-10},{10,10}},
            rotation=90,
            origin={0,110})));
    equation
      connect(demand.port_b, indirectStation.port_a2) annotation (Line(points={{-10,-60},
              {-20,-60},{-20,-30.5455},{-10,-30.5455}},      color={0,127,255}));
      connect(demand.port_a, indirectStation.port_b2) annotation (Line(points={{10,-60},
              {20,-60},{20,-30.5455},{10,-30.5455}}, color={0,127,255}));
      connect(port_a, indirectStation.port_b1) annotation (Line(points={{-100,0},
              {-54,0},{-54,-19.6364},{-10,-19.6364}},color={0,127,255}));
      connect(port_b, indirectStation.port_a1) annotation (Line(points={{100,0},
              {56,0},{56,-19.6364},{10,-19.6364}},color={0,127,255}));
      connect(senRelPre.port_b, port_a) annotation (Line(points={{-10,20},{-54,
              20},{-54,0},{-100,0}},color={0,127,255}));
      connect(senRelPre.port_a, port_b) annotation (Line(points={{10,20},{56,20},
              {56,0},{100,0}},color={0,127,255}));
      connect(senRelPre.p_rel, dp)
        annotation (Line(points={{0,29},{0,110}}, color={0,0,127}));
      annotation (
        Icon(
          coordinateSystem(preserveAspectRatio=false),
          graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={227,221,16},
              fillPattern=FillPattern.Solid,
              radius=15),
            Ellipse(
              extent={{-88,88},{88,-88}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Bitmap(
              extent={{-64,-46},{68,32}}, fileName=
                  "modelica://ERIGridMultiEnergyBenchmark/images/consumer.svg"),
            Polygon(
              points={{-132,92},{-132,92}},
              lineColor={0,0,0},
              lineThickness=0.5,
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid)}),
        Diagram(coordinateSystem(preserveAspectRatio=false)));
    end ConsumerSubstation;

    model ExternalGridMassFlowControlled
      "Mass flow-controlled external thermal grid."
      extends IBPSA.Fluid.Interfaces.PartialTwoPortInterface(
        redeclare package Medium = IBPSA.Media.Water,
        m_flow_nominal=10);

      Modelica.Blocks.Sources.RealExpression m_flow_set(
        y=Utility.clamp(0,m_flow_request,m_flow_nominal))
        annotation (Placement(transformation(extent={{-10,-80},{10,-60}})));
      IBPSA.Fluid.Sources.Boundary_pT bou(
        redeclare package Medium = IBPSA.Media.Water,
        p=200000,
        T=T_return_nominal,
        nPorts=1)
        annotation (Placement(transformation(extent={{10,-10},{-10,10}},
            rotation=-90,
            origin={-30,-30})));
      IBPSA.Fluid.Sources.MassFlowSource_T boundary(
        redeclare package Medium = IBPSA.Media.Water,
        use_m_flow_in=true,
        T=T_supply_nominal,
        nPorts=1)
        annotation (Placement(transformation(extent={{-10,-10},{10,10}},
            rotation=90,
            origin={30,-30})));
      IBPSA.Fluid.Sensors.EntropyFlowRate sflow_supply(redeclare package Medium =
        IBPSA.Media.Water, m_flow_nominal=m_flow_nominal,
        tau=0)
        annotation (Placement(transformation(extent={{50,10},{70,-10}})));
      IBPSA.Fluid.Sensors.EntropyFlowRate sflow_return(
        redeclare package Medium = IBPSA.Media.Water,
        m_flow_nominal=m_flow_nominal,
        tau=0)
        annotation (Placement(transformation(extent={{-70,10},{-50,-10}})));
      IBPSA.Fluid.Sensors.Temperature T_return(redeclare package Medium =
        IBPSA.Media.Water)
        annotation (Placement(transformation(extent={{-90,20},{-70,40}})));
      Modelica.Blocks.Interfaces.RealInput m_flow_request
        annotation (Placement(
            transformation(
            extent={{-20,-20},{20,20}},
            rotation=-90,
            origin={0,120})));

      parameter Modelica.SIunits.Temperature T_supply_nominal(displayUnit="degC") = 348.15 "Nominal supply temperature";
      parameter Modelica.SIunits.Temperature T_return_nominal(displayUnit="degC") = 313.15 "Nominal return temperature";
      parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal(displayUnit="kW") = 2000000 "Nominal heat flow rate";

      Modelica.SIunits.Heat Q_total_supply(start=0,displayUnit="kWh");
      Modelica.SIunits.Heat Q_total_return(start=0,displayUnit="kWh");

    equation

      der(Q_total_supply) = T_supply_nominal*sflow_supply.S_flow;
      der(Q_total_return) = T_return.T*sflow_return.S_flow;

      connect(boundary.m_flow_in, m_flow_set.y) annotation (Line(points={{22,-42},{22,
              -70},{11,-70}},        color={0,0,127}));
      connect(port_b,sflow_supply. port_b)
        annotation (Line(points={{100,0},{70,0}}, color={0,127,255}));
      connect(port_a, T_return.port)
        annotation (Line(points={{-100,0},{-80,0},{-80,20}}, color={0,127,255}));
      connect(sflow_return.port_b, bou.ports[1])
        annotation (Line(points={{-50,0},{-30,0},{-30,-20}},
                                                  color={0,127,255}));
      connect(sflow_supply.port_a, boundary.ports[1])
        annotation (Line(points={{50,0},{30,0},{30,-20}}, color={0,127,255}));
      connect(port_a, sflow_return.port_a)
        annotation (Line(points={{-100,0},{-70,0}}, color={0,127,255}));
      annotation (Icon(graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={227,221,16},
              fillPattern=FillPattern.Solid,
              radius=15),
            Ellipse(
              extent={{-88,89},{88,-87}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Bitmap(extent={{-56,-66},{58,8}}, fileName=
                  "modelica://ERIGridMultiEnergyBenchmark/images/external-grid.svg"),
            Text(
              extent={{-62,88},{64,2}},
              lineColor={0,0,0},
              pattern=LinePattern.None,
              fillColor={0,0,0},
              fillPattern=FillPattern.None,
              textString="m"),
            Ellipse(
              extent={{-4,76},{6,66}},
              lineColor={0,0,0},
              pattern=LinePattern.None,
              fillColor={0,0,0},
              fillPattern=FillPattern.Solid)}));
    end ExternalGridMassFlowControlled;

    model ExternalGridPressureControlled
     "Pressure-controlled external thermal grid."
      extends IBPSA.Fluid.Interfaces.PartialTwoPortInterface(
        redeclare package Medium = IBPSA.Media.Water,
        m_flow_nominal=10);

      DisHeatLib.Supply.Supply_pT supply_pT(
        redeclare package Medium = IBPSA.Media.Water,
        show_T=true,
        Q_flow_nominal(displayUnit="MW") = 2000000,
        TemSup_nominal=348.15,
        TemRet_nominal=313.15,
        isElectric=false,
        powerCha(Q_flow={0}, P={0}),
        dp_nominal(displayUnit="bar") = 600000,
        SupplyTemperature=DisHeatLib.Supply.BaseClasses.InputTypeSupplyTemp.Constant,
        TemOut_min=283.15,
        TemOut_max=283.15,
        TemSup_min=283.15,
        TemSup_max=283.15,
        dp_controller=true,
        dp_min=50000,
        dp_set=80000,
        dp_max=200000,
        ports_b,
        heater(show_T=true),
        nPorts=1)
        annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
      IBPSA.Fluid.Sensors.EntropyFlowRate sflow_supply(redeclare package Medium =
            IBPSA.Media.Water, m_flow_nominal=m_flow_nominal)
        annotation (Placement(transformation(extent={{60,-10},{80,10}})));
      IBPSA.Fluid.Sensors.Temperature T_supply(redeclare package Medium =
            IBPSA.Media.Water)
        annotation (Placement(transformation(extent={{30,20},{50,40}})));
      Modelica.Blocks.Interfaces.RealInput dp_measure annotation (Placement(
            transformation(
            extent={{-20,-20},{20,20}},
            rotation=-90,
            origin={0,120})));

      parameter Modelica.SIunits.Temperature T_supply_nominal(displayUnit="degC") = 348.15 "Nominal supply temperature";
      parameter Modelica.SIunits.Temperature T_return_nominal(displayUnit="degC") = 313.15 "Nominal return temperature";
      parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal(displayUnit="kW") = 2000000 "Nominal heat flow rate";

      Modelica.SIunits.Heat Q_total_supply(start=0,displayUnit="kWh");
      Modelica.SIunits.Heat Q_total_return(start=0,displayUnit="kWh");

      IBPSA.Fluid.Sensors.EntropyFlowRate sflow_return(redeclare package Medium =
            IBPSA.Media.Water, m_flow_nominal=m_flow_nominal)
        annotation (Placement(transformation(extent={{-82,-10},{-62,10}})));
      IBPSA.Fluid.Sensors.Temperature T_return(redeclare package Medium =
            IBPSA.Media.Water)
        annotation (Placement(transformation(extent={{-50,20},{-30,40}})));
    equation

      der(Q_total_supply) = T_supply.T*sflow_supply.S_flow;
      der(Q_total_return) = T_return.T*sflow_return.S_flow;

      connect(port_b,sflow_supply. port_b)
        annotation (Line(points={{100,0},{80,0}}, color={0,127,255}));
      connect(sflow_supply.port_a, supply_pT.ports_b[1])
        annotation (Line(points={{60,0},{10,0}},  color={0,127,255}));
      connect(supply_pT.dp_measure, dp_measure) annotation (Line(points={{-6,12},{-6,
              20},{0,20},{0,120}}, color={0,0,127}));
      connect(sflow_supply.port_a, T_supply.port)
        annotation (Line(points={{60,0},{40,0},{40,20}},color={0,127,255}));
      connect(port_a, sflow_return.port_a)
        annotation (Line(points={{-100,0},{-82,0}}, color={0,127,255}));
      connect(sflow_return.port_b, supply_pT.port_a)
        annotation (Line(points={{-62,0},{-10,0}}, color={0,127,255}));
      connect(sflow_return.port_b, T_return.port)
        annotation (Line(points={{-62,0},{-40,0},{-40,20}}, color={0,127,255}));
      annotation (Icon(graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={227,221,16},
              fillPattern=FillPattern.Solid,
              radius=15),
            Ellipse(
              extent={{-88,89},{88,-87}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Bitmap(extent={{-56,-66},{58,8}}, fileName=
                  "modelica://ERIGridMultiEnergyBenchmark/images/external-grid.svg"),
            Text(
              extent={{-62,88},{64,2}},
              lineColor={0,0,0},
              pattern=LinePattern.None,
              fillColor={0,0,0},
              fillPattern=FillPattern.None,
              textString="P")}));
    end ExternalGridPressureControlled;

    model Heatpump
      "Heat pump used in the power-to-heat facility."
      extends IBPSA.Fluid.Interfaces.PartialFourPortInterface(
      redeclare package Medium1 = IBPSA.Media.Water,
      redeclare package Medium2 = IBPSA.Media.Water);

      IBPSA.Fluid.HeatExchangers.HeaterCooler_u evaporator(
        redeclare package Medium = IBPSA.Media.Water,
        m_flow_nominal=10,
        show_T=false,
        dp_nominal=1000,
        T_start=333.15,
        Q_flow_nominal(displayUnit="kW") = -Q_flow_evaporator_rated)
        annotation (Placement(transformation(extent={{10,-40},{-10,-20}})));
      IBPSA.Fluid.HeatExchangers.Heater_T condenser(
        redeclare package Medium = IBPSA.Media.Water,
        m_flow_nominal=10,
        show_T=false,
        dp_nominal(displayUnit="bar") = 10000)
        annotation (Placement(transformation(extent={{-10,20},{10,40}})));
      IBPSA.Fluid.Sensors.Temperature TcondIn(redeclare package Medium =
            IBPSA.Media.Water)
        annotation (Placement(transformation(extent={{-86,46},{-74,34}})));
      IBPSA.Fluid.Sensors.Temperature TcondOut(redeclare package Medium =
            IBPSA.Media.Water)
        annotation (Placement(transformation(extent={{86,46},{74,34}})));
      IBPSA.Fluid.Sensors.Temperature TevapIn(redeclare package Medium =
            IBPSA.Media.Water)
        annotation (Placement(transformation(extent={{86,-46},{74,-34}})));
      IBPSA.Fluid.Sensors.Temperature TevapOut(redeclare package Medium =
            IBPSA.Media.Water)
        annotation (Placement(transformation(extent={{-86,-46},{-74,-34}})));
      Modelica.Blocks.Sources.RealExpression P_effective(y=P_0 + W_effective/eta_comp)
        annotation (Placement(transformation(extent={{-60,-90},{-20,-70}})));
      Modelica.Blocks.Sources.RealExpression T_cond_set(y=T_cond_out_target)
        annotation (Placement(transformation(extent={{-80,70},{-40,90}})));
      Modelica.Blocks.Sources.RealExpression u_evap(y=abs((1 - eta)*W_effective/Q_flow_evaporator_rated))
        annotation (Placement(transformation(extent={{80,-8},{40,10}})));
      Modelica.Blocks.Interfaces.RealOutput P_el_heatpump annotation (Placement(
            transformation(
            extent={{-10,-10},{10,10}},
            rotation=-90,
            origin={0,-110})));

      parameter Modelica.SIunits.HeatFlowRate Q_flow_evaporator_rated(displayUnit="kW") = 100000
        "Heat flow rating at evaporator";

      parameter Modelica.SIunits.Power P_rated(displayUnit="kW") = 100000.0 "Electrical power rating";
      parameter Modelica.SIunits.Power P_0(displayUnit="kW") = 300 "Electrical stand-by power consumption";

      parameter Modelica.SIunits.Temperature T_evap_out_min(displayUnit="degC") = 288.15 "Minimal evaporator outlet temperature";
      parameter Modelica.SIunits.Temperature T_cond_out_max(displayUnit="degC") = 358.15 "Maximum condenser outlet temperature";
      parameter Modelica.SIunits.Temperature T_cond_out_target(displayUnit="degC") = 348.15 "Condenser outlet temperature setpoint";

      parameter Modelica.SIunits.Efficiency eta_sys = 0.63 "Ratio between work provided by the pump and available thermodynamic work";
      parameter Modelica.SIunits.Efficiency eta_comp = 0.65 "Compressor efficiency";
      parameter Modelica.SIunits.DampingCoefficient lambda_comp = 0.05 "Compressor time constant";

      Modelica.SIunits.Power W_cond_max "Maximum mechanical work done in the condenser";
      Modelica.SIunits.Power W_evap_max "Maximum mechanical work done in the evaporator";
      Modelica.SIunits.Power W_max "Maximum mechanical work constraint";
      Modelica.SIunits.Power W_requested "Requested mechanical work";
      Modelica.SIunits.Power W_effective "Effective mechanical work";

      Modelica.SIunits.Temperature T_cond_log "Logarithmic mean temperature of condenser";
      Modelica.SIunits.Temperature T_evap_log "Logarithmic mean temperature of evaporator";
      Modelica.SIunits.Efficiency eta "Overall efficiency";

    protected
      parameter Modelica.SIunits.Power W_rated(fixed = false) "Mechanical power rating";
      parameter Modelica.SIunits.Power W_0(fixed = false) "Mechanical stand-by power consumption";
      parameter Modelica.SIunits.SpecificHeatCapacity cp_cond(fixed = false)
        "Specific heat capacity of medium 1 at nominal condition";
      parameter Modelica.SIunits.SpecificHeatCapacity cp_evap(fixed = false)
        "Specific heat capacity of medium 2 at nominal condition";

    initial equation
      W_rated = P_rated * eta_comp;
      W_0 = P_0 * eta_comp;

      cp_cond = Medium1.specificHeatCapacityCp(state_a1_inflow);
      cp_evap = Medium2.specificHeatCapacityCp(state_a2_inflow);

    equation
      T_cond_log = Utility.logMean(TcondIn.T, TcondOut.T);
      T_evap_log = Utility.logMean(TevapIn.T, TevapOut.T);

      eta = Utility.eta(T_evap_log, T_cond_log, eta_sys);

      W_cond_max = (T_cond_out_max - TcondIn.T) * cp_cond * m1_flow / eta;
      W_evap_max = (TevapIn.T - T_evap_out_min) * cp_evap * m2_flow / (eta - 1);
      W_max = max(0.0, min([W_evap_max, W_cond_max, W_rated]));
      W_requested = Utility.clamp(0, condenser.Q_flow/eta, W_max);

      der(W_effective) = lambda_comp * (W_requested - W_effective);

      connect(port_a2, evaporator.port_a)
        annotation (Line(points={{100,-60},{40,-60},{40,-30},{10,-30}},color={0,127,255}));
      connect(evaporator.port_b, port_b2)
        annotation (Line(points={{-10,-30},{-40,-30},{-40,-60},{-100,-60}},color={0,127,255}));
      connect(port_a1, condenser.port_a)
        annotation (Line(points={{-100,60},{-40,60},{-40,30},{-10,30}},color={0,127,255}));
      connect(port_b1, condenser.port_b)
        annotation (Line(points={{100,60},{40,60},{40,30},{10,30}},color={0,127,255}));
      connect(port_a1, TcondIn.port)
        annotation (Line(points={{-100,60},{-80,60},{-80,46}}, color={0,127,255}));
      connect(port_b1, TcondOut.port)
        annotation (Line(points={{100,60},{80,60},{80,46}}, color={0,127,255}));
      connect(TevapIn.port, port_a2)
        annotation (Line(points={{80,-46},{80,-60},{100,-60}}, color={0,127,255}));
      connect(port_b2, TevapOut.port) annotation (Line(points={{-100,-60},{-80,-60},
              {-80,-46}}, color={0,127,255}));
      connect(condenser.TSet, T_cond_set.y) annotation (Line(points={{-12,38},{-30,38},
              {-30,80},{-38,80}}, color={0,0,127}));
      connect(P_el_heatpump, P_effective.y)
        annotation (Line(points={{0,-110},{0,-80},{-18,-80}}, color={0,0,127}));
      connect(evaporator.u, u_evap.y) annotation (Line(points={{12,-24},{30,-24},{30,
              1},{38,1}}, color={0,0,127}));
      annotation (Icon(graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={227,221,16},
              fillPattern=FillPattern.Solid,
              radius=15),
            Ellipse(
              extent={{-88,88},{88,-88}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Bitmap(extent={{-58,-60},{64,58}}, fileName=
                  "modelica://ERIGridMultiEnergyBenchmark/images/heat-pump.svg"),
            Rectangle(
              extent={{-100,66},{0,54}},
              lineThickness=1,
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid,
              pattern=LinePattern.None,
              lineColor={0,0,0}),
            Rectangle(
              extent={{0,-54},{100,-66}},
              lineThickness=1,
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid,
              pattern=LinePattern.None,
              lineColor={0,0,0}),
            Rectangle(
              extent={{0,66},{100,54}},
              lineThickness=1,
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid,
              pattern=LinePattern.None,
              lineColor={0,0,0}),
            Rectangle(
              extent={{-100,-54},{0,-66}},
              lineThickness=1,
              fillColor={0,0,173},
              fillPattern=FillPattern.Solid,
              pattern=LinePattern.None,
              lineColor={0,0,0})}));
    end Heatpump;

    model PowerToHeat
      "Power-to-heat facility with heat pump and tank."
      extends IBPSA.Fluid.Interfaces.PartialFourPortInterface(
        m1_flow_nominal = 10,
        m2_flow_nominal = 10,
        redeclare package Medium1 = IBPSA.Media.Water,
        redeclare package Medium2 = IBPSA.Media.Water);

      IBPSA.Fluid.FixedResistances.Junction junction_n3s(
        redeclare package Medium = IBPSA.Media.Water,
        m_flow_nominal={-20,10,10},
        dp_nominal={-10,10,10})
      annotation (Placement(transformation(extent={{60,50},{80,70}})));
      IBPSA.Fluid.FixedResistances.Junction junction_n3r(
        redeclare package Medium = IBPSA.Media.Water,
        m_flow_nominal={20,-10,-10},
        dp_nominal={10,-10,-10})
      annotation (Placement(transformation(extent={{82,-50},{62,-70}})));
      IBPSA.Fluid.Movers.FlowControlled_m_flow pump(
        redeclare package Medium = IBPSA.Media.Water,
        energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial,
        m_flow_nominal=2,
        redeclare IBPSA.Fluid.Movers.Data.Pumps.Wilo.Stratos80slash1to12 per,
        inputType=IBPSA.Fluid.Types.InputType.Continuous,
        addPowerToMedium=false,
        riseTime(displayUnit="min"),
        nominalValuesDefineDefaultPressureCurve=true,
        dp_nominal(displayUnit="bar") = 10000,
        constantMassFlowRate=0.1)
      annotation (Placement(transformation(extent={{-10,10},{10,-10}},
            rotation=0,
            origin={10,20})));
      IBPSA.Fluid.Movers.FlowControlled_m_flow fan(
        redeclare package Medium = IBPSA.Media.Water,
        m_flow_nominal=storageTank.m_flow_nominal,
        redeclare IBPSA.Fluid.Movers.Data.Pumps.Wilo.Stratos80slash1to12 per,
        inputType=IBPSA.Fluid.Types.InputType.Continuous)
      annotation (Placement(transformation(extent={{-50,22},{-70,42}})));
      DisHeatLib.Storage.StorageTank storageTank(
        show_T=true,
        redeclare package Medium = IBPSA.Media.Water,
        VTan=86,
        hTan=7.9,
        dIns=0.1,
        kIns=0.03,
        nSeg=nTankSegments,
        TemInit=343.15,
        TemRoom=288.15,
        m_flow_nominal=5)
      annotation (Placement(transformation(extent={{-20,16},{-40,36}})));
      DisHeatLib.Pipes.DualPipe pipe_l1_tank(
        show_T=true,
        redeclare package Medium = IBPSA.Media.Water,
        redeclare DisHeatLib.Pipes.Library.Isoplus.Isoplus_Std_DN100 pipeType,
        L=10,
        nPorts2=1,
        nPorts1=1)
      annotation (Placement(transformation(extent={{40,-40},{60,-20}})));
      Heatpump heatpump(
        m1_flow_nominal=storageTank.m_flow_nominal,
        m2_flow_nominal=junction_n3r.m_flow_nominal[1],
        Q_flow_evaporator_rated=Q_flow_evaporator_rated,
        P_rated=P_rated)
      annotation (Placement(transformation(extent={{-40,-64},{-20,-44}})));
      Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a port_ht
      annotation (Placement(transformation(extent={{-10,90},{10,110}})));
      Modelica.Blocks.Interfaces.RealInput mdot_tank_out annotation (Placement(
            transformation(
              extent={{-20,-20},{20,20}},
              rotation=90,
              origin={-50,-110})));
      Modelica.Blocks.Interfaces.RealInput mdot_condenser_in annotation (Placement(
            transformation(
              extent={{-20,-20},{20,20}},
              rotation=90,
              origin={-90,-110})));
      Modelica.Blocks.Interfaces.RealOutput T_tank_low annotation (Placement(
            transformation(
              extent={{-10,-11},{10,11}},
              rotation=-90,
              origin={60,-105})));
      Modelica.Blocks.Interfaces.RealOutput T_tank_high annotation (Placement(
            transformation(
              extent={{-10,-11},{10,11}},
              rotation=-90,
              origin={90,-105})));
      Modelica.Blocks.Interfaces.RealOutput P_el_heatpump annotation (Placement(
            transformation(
              extent={{-10,-11},{10,11}},
              rotation=-90,
              origin={30,-105})));
      Modelica.Blocks.Interfaces.RealOutput E_el_heatpump_consumed annotation (Placement(
            transformation(
              extent={{-10,-11},{10,11}},
              rotation=-90,
              origin={0,-105})));

      parameter Modelica.SIunits.HeatFlowRate Q_flow_evaporator_rated(displayUnit="kW") = 500000 "Heat flow rating at evaporator";
      parameter Modelica.SIunits.Power P_rated(displayUnit="kW") = 100000.0 "Electrical power rating";
      Modelica.SIunits.Energy E_el_heatpump_total(start=0);

      parameter Integer nTankSegments=10 "Number of segments in tank model";
      parameter Integer nTankSenseTempHigh=2 "Position of upper tank temperature sensor (number of tank segment)";
      parameter Integer nTankSenseTempLow=9 "Position of lower tank temperature sensor (number of tank segment)";

      Real T_tank_mean_degC "Mean tank temperature in °C";

    equation

      der(E_el_heatpump_total) = heatpump.P_el_heatpump;
      E_el_heatpump_consumed = E_el_heatpump_total;

      T_tank_mean_degC = sum(storageTank.TemTank) / nTankSegments - 273.15;

      connect(junction_n3s.port_2, port_b1)
      annotation (Line(points={{80,60},{100,60}}, color={0,127,255}));
      connect(storageTank.port_b2, pump.port_a)
      annotation (Line(points={{-20,20},{0,20}},           color={0,127,255}));
      connect(storageTank.port_b1, fan.port_a)
      annotation (Line(points={{-40,32},{-50,32}}, color={0,127,255}));
      connect(mdot_tank_out, pump.m_flow_in) annotation (Line(points={{-50,-110},{-50,
                -70},{10,-70},{10,8}},color={0,0,127}));
      connect(fan.m_flow_in, mdot_condenser_in) annotation (Line(points={{-60,44},
              {-60,50},{-90,50},{-90,-110}},color={0,0,127}));
      connect(T_tank_low, storageTank.TemTank[nTankSenseTempLow]) annotation (Line(points={{60,-105},
              {60,-80},{90,-80},{90,-10},{-30,-10},{-30,15}},    color={0,0,127}));
      connect(T_tank_high, storageTank.TemTank[nTankSenseTempHigh]) annotation (Line(points={{90,-105},
              {90,-10},{-30,-10},{-30,15}},   color={0,0,127}));
      connect(pump.port_b, pipe_l1_tank.port_a1) annotation (Line(points={{20,
              20},{30,20},{30,-24},{40,-24}}, color={0,127,255}));
      connect(pipe_l1_tank.ports_b1[1], junction_n3s.port_3) annotation (Line(
            points={{60,-24},{70,-24},{70,50}}, color={0,127,255}));
      connect(junction_n3r.port_3, pipe_l1_tank.port_a2) annotation (Line(
            points={{72,-50},{72,-36},{60,-36}}, color={0,127,255}));
      connect(pipe_l1_tank.ports_b2[1], storageTank.port_a2) annotation (Line(
            points={{40,-36},{-50,-36},{-50,20},{-40,20}}, color={0,127,255}));
      connect(port_ht, pipe_l1_tank.port_ht) annotation (Line(points={{0,100},{
              0,50},{50,50},{50,-20}}, color={191,0,0}));
      connect(junction_n3r.port_1, port_a2)
      annotation (Line(points={{82,-60},{100,-60}}, color={0,127,255}));
      connect(port_a1, junction_n3s.port_1)
      annotation (Line(points={{-100,60},{60,60}}, color={0,127,255}));
      connect(heatpump.port_b1, storageTank.port_a1) annotation (Line(points={{-20,-48},
                {-10,-48},{-10,32},{-20,32}}, color={0,127,255}));
      connect(fan.port_b, heatpump.port_a1) annotation (Line(points={{-70,32},{-80,32},
                {-80,-48},{-40,-48}}, color={0,127,255}));
      connect(port_b2, heatpump.port_b2)
      annotation (Line(points={{-100,-60},{-40,-60}}, color={0,127,255}));
      connect(heatpump.port_a2, junction_n3r.port_2)
      annotation (Line(points={{-20,-60},{62,-60}}, color={0,127,255}));
      connect(heatpump.P_el_heatpump, P_el_heatpump) annotation (Line(points={{-30,-65},
                {-30,-80},{30,-80},{30,-105}}, color={0,0,127}));

      annotation (
        Icon(
          coordinateSystem(preserveAspectRatio=false),
          graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={227,221,16},
              fillPattern=FillPattern.Solid,
              radius=15),
            Ellipse(
              extent={{-88,88},{88,-88}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Bitmap(
              extent={{-62,-68},{64,68}}, fileName=
                  "modelica://ERIGridMultiEnergyBenchmark/images/power-to-heat.svg")}),
        Diagram(coordinateSystem(preserveAspectRatio=false)));
    end PowerToHeat;

    package Utility
      "Helper functions."
      function logMean "Logarithmic mean of two values"
        extends Modelica.Icons.Function;
        input Real a "First input value";
        input Real b "Second input value";
        output Real y "Result";

      protected
        Real delta = a - b;

      algorithm
          if abs(delta) > 1e-3 then
            y := delta / log(a/b);
          else
            y := a - delta/2*(1 + delta/6/a*(1 + delta/2/a));
          end if;

      end logMean;

      function clamp
        "Ensure that value x lies within the closed interval [a, b]"
        extends Modelica.Icons.Function;
        input Real a "Closed interval left limit";
        input Real x "Value limited by closed interval [a, b]";
        input Real b "Closed interval right limit";
        output Real y "Result";

      algorithm

        if x > a then
          if x < b then
            y := x;
          else
            y := b;
          end if;
        else
          y := a;
        end if;

      end clamp;

      function eta
        "Compute overall heat pump effciency"
        extends Modelica.Icons.Function;
        input Real T_evap_log "Evaporator log mean temperature";
        input Real T_cond_log "Condenser log mean temperature";
        input Real eta_sys "Relation between work provided by the pump and available thermodynamic work";
        output Real y "Result";

      algorithm
        if T_evap_log < T_cond_log then
          y := eta_sys/(1 - T_evap_log/T_cond_log);
        else
          y := Modelica.Constants.inf;
        end if;

      end eta;
      annotation (Icon(graphics={
            Rectangle(
              lineColor={200,200,200},
              fillColor={248,248,248},
              fillPattern=FillPattern.HorizontalCylinder,
              extent={{-100,-100},{100,100}},
              radius=25),                  Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              radius=25),
        Polygon(
          origin={-2.6165,-0.1418},
          rotation=45.0,
          fillColor={64,64,64},
          pattern=LinePattern.None,
          fillPattern=FillPattern.Solid,
          points={{-15.0,93.333},{-15.0,68.333},{0.0,58.333},{15.0,68.333},{15.0,93.333},{20.0,93.333},{25.0,83.333},{25.0,58.333},{10.0,43.333},{10.0,-41.667},{25.0,-56.667},{25.0,-76.667},{10.0,-91.667},{0.0,-91.667},{0.0,-81.667},{5.0,-81.667},{15.0,-71.667},{15.0,-61.667},{5.0,-51.667},{-5.0,-51.667},{-15.0,-61.667},{-15.0,-71.667},{-5.0,-81.667},{0.0,-81.667},{0.0,-91.667},{-10.0,-91.667},{-25.0,-76.667},{-25.0,-56.667},{-10.0,-41.667},{-10.0,43.333},{-25.0,58.333},{-25.0,83.333},{-20.0,93.333}}),
        Polygon(
          origin={6.1018,9.218},
          rotation=-45.0,
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid,
          points={{-15.0,87.273},{15.0,87.273},{20.0,82.273},{20.0,27.273},{10.0,17.273},{10.0,7.273},{20.0,2.273},{20.0,-2.727},{5.0,-2.727},{5.0,-77.727},{10.0,-87.727},{5.0,-112.727},{-5.0,-112.727},{-10.0,-87.727},{-5.0,-77.727},{-5.0,-2.727},{-20.0,-2.727},{-20.0,2.273},{-10.0,7.273},{-10.0,17.273},{-20.0,27.273},{-20.0,82.273}})}));
    end Utility;
    annotation (Icon(graphics={
          Rectangle(
            lineColor={200,200,200},
            fillColor={248,248,248},
            fillPattern=FillPattern.HorizontalCylinder,
            extent={{-100,-100},{100,100}},
            radius=25),                  Rectangle(
            extent={{-100,100},{100,-100}},
            lineColor={0,0,0},
            radius=25),
          Bitmap(extent={{-64,-76},{76,64}}, fileName=
                "modelica://ERIGridMultiEnergyBenchmark/images/gears.svg")}));
  end Components;

  package Examples

    model DHNetworkMassFlowControlled_Test

      Modelica.Blocks.Sources.Constant valve_grid_v1_setpoint(k=1) annotation (
          Placement(transformation(
            extent={{10,-10},{-10,10}},
            rotation=0,
            origin={20,-80})));
      Modelica.Blocks.Sources.Constant P_el_heatpump_on(k=100000)
        annotation (Placement(transformation(extent={{70,-70},{50,-50}})));
      Modelica.Blocks.Sources.Constant P_el_heatpump_off(k=0)
        annotation (Placement(transformation(extent={{70,-30},{50,-10}})));
      Modelica.Blocks.Sources.Constant mdot_tank_off(k=0)
        annotation (Placement(transformation(extent={{70,0},{50,20}})));
      Modelica.Blocks.Sources.Constant mdot_tank_on(k=2)
        annotation (Placement(transformation(extent={{70,40},{50,60}})));
      Modelica.Blocks.Logical.Switch P_el_heatpump_set_switch
        annotation (Placement(transformation(extent={{30,-50},{10,-30}})));
      Modelica.Blocks.Logical.Switch mdot_tank_switch
        annotation (Placement(transformation(extent={{30,20},{10,40}})));
      Modelica.Blocks.Logical.Hysteresis hysteresis(uLow=273.15 + 65, uHigh=
            273.15 + 72)
        annotation (Placement(transformation(extent={{10,70},{30,90}})));
      Modelica.Blocks.Continuous.LimPID PID_controller(
        controllerType=Modelica.Blocks.Types.SimpleController.PID,
        k=1e-4,
        Ti=10,
        Td=10,
        yMax=5,
        yMin=0,
        withFeedForward=false)
        annotation (Placement(transformation(extent={{0,-30},{-20,-50}})));
      DHNetworkMassFlowControlled thermalNetwork(fileNameConsumer2=
            "modelica://ERIGridMultiEnergyBenchmark/data/heat_demand_load_profile_consumer1_1week.txt",
          fileNameConsumer1=
            "modelica://ERIGridMultiEnergyBenchmark/data/heat_demand_load_profile_consumer2_1week.txt")
        annotation (Placement(transformation(
            extent={{-30,-19},{30,19}},
            rotation=90,
            origin={-71,0})));

    equation
      connect(P_el_heatpump_set_switch.y, PID_controller.u_s)
        annotation (Line(points={{9,-40},{2,-40}}, color={0,0,127}));
      connect(valve_grid_v1_setpoint.y,thermalNetwork. valve_grid_v1_setpoint)
        annotation (Line(points={{9,-80},{-40,-80},{-40,-25.2632},{-50.7333,
              -25.2632}},
            color={0,0,127}));
      connect(hysteresis.u,thermalNetwork. T_tank_high) annotation (Line(points={{8,80},{
              -40,80},{-40,23.6842},{-50.4167,23.6842}},
                                                color={0,0,127}));
      connect(mdot_tank_switch.y,thermalNetwork. mdot_tank_out) annotation (
          Line(points={{9,30},{-30,30},{-30,-6.31579},{-50.7333,-6.31579}},
                                                           color={0,0,127}));
      connect(thermalNetwork.P_el_heatpump, PID_controller.u_m) annotation (
          Line(points={{-50.4167,4.73684},{-10,4.73684},{-10,-28}}, color={0,0,
              127}));
      connect(PID_controller.y, thermalNetwork.mdot_condenser_in) annotation (
          Line(points={{-21,-40},{-30,-40},{-30,-15.7895},{-50.7333,-15.7895}},
            color={0,0,127}));
      connect(mdot_tank_off.y, mdot_tank_switch.u3) annotation (Line(points={{
              49,10},{40,10},{40,22},{32,22}}, color={0,0,127}));
      connect(mdot_tank_switch.u1, mdot_tank_on.y) annotation (Line(points={{32,
              38},{40,38},{40,50},{49,50}}, color={0,0,127}));
      connect(P_el_heatpump_set_switch.u1, P_el_heatpump_off.y) annotation (
          Line(points={{32,-32},{40,-32},{40,-20},{49,-20}}, color={0,0,127}));
      connect(P_el_heatpump_set_switch.u3, P_el_heatpump_on.y) annotation (Line(
            points={{32,-48},{40,-48},{40,-60},{49,-60}}, color={0,0,127}));
      connect(P_el_heatpump_set_switch.u2, hysteresis.y) annotation (Line(
            points={{32,-40},{80,-40},{80,80},{31,80}}, color={255,0,255}));
      connect(mdot_tank_switch.u2, hysteresis.y) annotation (Line(points={{32,
              30},{80,30},{80,80},{31,80}}, color={255,0,255}));
      annotation (
        Icon(
          coordinateSystem(preserveAspectRatio=false),
          graphics={
            Ellipse(lineColor = {75,138,73},
                    fillColor={255,255,255},
                    fillPattern = FillPattern.Solid,
                    extent={{-100,-100},{100,100}}),
            Polygon(lineColor = {0,0,255},
                    fillColor = {75,138,73},
                    pattern = LinePattern.None,
                    fillPattern = FillPattern.Solid,
                    points={{-36,60},{64,0},{-36,-60},{-36,60}})}),
        Diagram(coordinateSystem(preserveAspectRatio=false)),
        experiment(StopTime=172800, __Dymola_Algorithm="Dassl"),
        Documentation(info="<html>
    <p>This model implements a simple controller for the power-to-heat facility (heat pump and tank) of the mass flow-regulated thermal system of the multi-energy network benchmark. A hysteresis controller keeps the tank temperature within a pre-defined range by turning the heat pump on/off. Whenever the heat pump is turned off, the tank is discharged to support the thermal network. The discharge mass flow rate of the tank is governed by a PI controller, which aims at operating the heat pump at a given power consumption setpoint.</p>
    </html>"));
    end DHNetworkMassFlowControlled_Test;

    model DHNetworkPressureControlled_Test

      Modelica.Blocks.Sources.Constant valve_grid_v1_setpoint(k=1) annotation (
          Placement(transformation(
            extent={{10,-10},{-10,10}},
            rotation=0,
            origin={20,-80})));
      Modelica.Blocks.Sources.Constant P_el_heatpump_on(k=100000)
        annotation (Placement(transformation(extent={{70,-70},{50,-50}})));
      Modelica.Blocks.Sources.Constant P_el_heatpump_off(k=0)
        annotation (Placement(transformation(extent={{70,-30},{50,-10}})));
      Modelica.Blocks.Sources.Constant mdot_tank_off(k=0)
        annotation (Placement(transformation(extent={{70,0},{50,20}})));
      Modelica.Blocks.Sources.Constant mdot_tank_on(k=2)
        annotation (Placement(transformation(extent={{70,40},{50,60}})));
      Modelica.Blocks.Logical.Switch P_el_heatpump_set_switch
        annotation (Placement(transformation(extent={{30,-50},{10,-30}})));
      Modelica.Blocks.Logical.Switch mdot_tank_switch
        annotation (Placement(transformation(extent={{30,20},{10,40}})));
      Modelica.Blocks.Logical.Hysteresis hysteresis(uLow=273.15 + 65, uHigh=
            273.15 + 72)
        annotation (Placement(transformation(extent={{10,70},{30,90}})));
      Modelica.Blocks.Continuous.LimPID PID_controller(
        controllerType=Modelica.Blocks.Types.SimpleController.PID,
        k=1e-4,
        Ti=10,
        Td=10,
        yMax=5,
        yMin=0,
        withFeedForward=false)
        annotation (Placement(transformation(extent={{0,-30},{-20,-50}})));
      DHNetworkPressureControlled thermalNetwork(fileNameConsumer2=
            "modelica://ERIGridMultiEnergyBenchmark/data/heat_demand_load_profile_consumer1_1week.txt",
          fileNameConsumer1=
            "modelica://ERIGridMultiEnergyBenchmark/data/heat_demand_load_profile_consumer2_1week.txt")
        annotation (Placement(transformation(
            extent={{-30,-19},{30,19}},
            rotation=90,
            origin={-71,0})));

    equation
      connect(P_el_heatpump_set_switch.y, PID_controller.u_s)
        annotation (Line(points={{9,-40},{2,-40}}, color={0,0,127}));
      connect(valve_grid_v1_setpoint.y,thermalNetwork. valve_grid_v1_setpoint)
        annotation (Line(points={{9,-80},{-40,-80},{-40,-25.2632},{-50.7333,
              -25.2632}},color={0,0,127}));
      connect(hysteresis.u,thermalNetwork. T_tank_high) annotation (Line(points={{8,80},{
              -40,80},{-40,23.6842},{-50.4167,23.6842}},color={0,0,127}));
      connect(mdot_tank_switch.y,thermalNetwork. mdot_tank_out) annotation (
          Line(points={{9,30},{-30,30},{-30,-6.31579},{-50.7333,-6.31579}},color={0,0,127}));
      connect(thermalNetwork.P_el_heatpump, PID_controller.u_m) annotation (
          Line(points={{-50.4167,4.73684},{-10,4.73684},{-10,-28}}, color={0,0,
              127}));
      connect(PID_controller.y, thermalNetwork.mdot_condenser_in) annotation (
          Line(points={{-21,-40},{-30,-40},{-30,-15.7895},{-50.7333,-15.7895}},
            color={0,0,127}));
      connect(mdot_tank_off.y, mdot_tank_switch.u3) annotation (Line(points={{
              49,10},{40,10},{40,22},{32,22}}, color={0,0,127}));
      connect(mdot_tank_switch.u1, mdot_tank_on.y) annotation (Line(points={{32,
              38},{40,38},{40,50},{49,50}}, color={0,0,127}));
      connect(P_el_heatpump_set_switch.u1, P_el_heatpump_off.y) annotation (
          Line(points={{32,-32},{40,-32},{40,-20},{49,-20}}, color={0,0,127}));
      connect(P_el_heatpump_set_switch.u3, P_el_heatpump_on.y) annotation (Line(
            points={{32,-48},{40,-48},{40,-60},{49,-60}}, color={0,0,127}));
      connect(P_el_heatpump_set_switch.u2, hysteresis.y) annotation (Line(
            points={{32,-40},{80,-40},{80,80},{31,80}}, color={255,0,255}));
      connect(mdot_tank_switch.u2, hysteresis.y) annotation (Line(points={{32,
              30},{80,30},{80,80},{31,80}}, color={255,0,255}));
      annotation (
        Icon(
          coordinateSystem(preserveAspectRatio=false), graphics={
            Ellipse(lineColor = {75,138,73},
                    fillColor={255,255,255},
                    fillPattern = FillPattern.Solid,
                    extent={{-100,-100},{100,100}}),
            Polygon(lineColor = {0,0,255},
                    fillColor = {75,138,73},
                    pattern = LinePattern.None,
                    fillPattern = FillPattern.Solid,
                    points={{-36,60},{64,0},{-36,-60},{-36,60}})}),
        Diagram(coordinateSystem(preserveAspectRatio=false)),
        experiment(StopTime=172800, __Dymola_Algorithm="Dassl"),
        Documentation(info="<html>
    <p>This model implements a simple controller for the power-to-heat facility (heat pump and tank) of the pressure-regulated thermal system of the multi-energy network benchmark. A hysteresis controller keeps the tank temperature within a pre-defined range by turning the heat pump on/off. Whenever the heat pump is turned off, the tank is discharged to support the thermal network. The discharge mass flow rate of the tank is governed by a PI controller, which aims at operating the heat pump at a given power consumption setpoint.</p>
    </html>"));
    end DHNetworkPressureControlled_Test;

    model HeatPump_Test "This is a test"
      IBPSA.Fluid.Sources.MassFlowSource_T source_condenser(
        redeclare package Medium = IBPSA.Media.Water,
        use_m_flow_in=true,
        m_flow=3.5,
        use_T_in=true,
        T=318.15,
        nPorts=1) annotation (Placement(transformation(extent={{-50,40},{-30,60}})));
      IBPSA.Fluid.Sources.MassFlowSource_T source_evaporator(
        redeclare package Medium = IBPSA.Media.Water,
        m_flow=10,
        use_T_in=true,
        T=318.15,
        nPorts=1) annotation (Placement(transformation(extent={{50,-20},{30,0}})));
      IBPSA.Fluid.Sources.Boundary_pT sink_condenser(
        redeclare package Medium = IBPSA.Media.Water,
        T=323.15,
        nPorts=1) annotation (Placement(transformation(extent={{50,40},{30,60}})));
      IBPSA.Fluid.Sources.Boundary_pT sink_evaporator(
        redeclare package Medium = IBPSA.Media.Water,
        p(displayUnit="bar"),
        T=323.15,
        nPorts=1) annotation (Placement(transformation(extent={{-50,-20},{-30,0}})));
      Components.Heatpump constantTcondHeatpump(
        m1_flow_nominal=3.5,
        m2_flow_nominal=10,
        condenser(show_T=true),
        evaporator(show_T=true),
        P_rated(displayUnit="kW"),
        T_evap_out_min(displayUnit="degC") = 293.15,
        T_cond_out_max=358.15,
        T_cond_out_target=348.15,
        eta_sys=0.5,
        eta_comp=0.7,
        lambda_comp=0.2)
        annotation (Placement(transformation(extent={{-10,10},{10,30}})));
      Modelica.Blocks.Sources.Step P_el_setpoint(
        height=30000,
        offset=70000,
        startTime=450)
        annotation (Placement(transformation(extent={{50,-60},{30,-40}})));
      Modelica.Blocks.Continuous.LimPID PI_controller(
        controllerType=Modelica.Blocks.Types.SimpleController.PI,
        yMax=5,
        yMin=0) annotation (Placement(transformation(extent={{10,-40},{-10,-60}})));
      Modelica.Blocks.Sources.Ramp T_condenser_in(
        height=10,
        duration=800,
        offset=273.15 + 45,
        startTime=100)
        annotation (Placement(transformation(extent={{-90,40},{-70,60}})));
      Modelica.Blocks.Sources.Pulse T_evaporator_in(
        amplitude=10,
        period=300,
        offset=273.15 + 40,
        startTime(displayUnit="ms"))
        annotation (Placement(transformation(extent={{90,-20},{70,0}})));
    equation
      connect(source_condenser.ports[1], constantTcondHeatpump.port_a1) annotation (
         Line(points={{-30,50},{-20,50},{-20,26},{-10,26}}, color={0,127,255}));
      connect(sink_condenser.ports[1], constantTcondHeatpump.port_b1) annotation (
          Line(points={{30,50},{20,50},{20,26},{10,26}}, color={0,127,255}));
      connect(sink_evaporator.ports[1], constantTcondHeatpump.port_b2) annotation (
          Line(points={{-30,-10},{-20,-10},{-20,14},{-10,14}}, color={0,127,255}));
      connect(source_evaporator.ports[1], constantTcondHeatpump.port_a2)
        annotation (Line(points={{30,-10},{20,-10},{20,14},{10,14}}, color={0,127,255}));
      connect(constantTcondHeatpump.P_el_heatpump, PI_controller.u_m)
        annotation (Line(points={{0,9},{0,-38}}, color={0,0,127}));
      connect(PI_controller.u_s, P_el_setpoint.y)
        annotation (Line(points={{12,-50},{29,-50}}, color={0,0,127}));
      connect(PI_controller.y, source_condenser.m_flow_in) annotation (Line(points={
              {-11,-50},{-60,-50},{-60,58},{-52,58}}, color={0,0,127}));
      connect(source_condenser.T_in, T_condenser_in.y) annotation (Line(points={{-52,
              54},{-64,54},{-64,50},{-69,50}}, color={0,0,127}));
      connect(source_evaporator.T_in, T_evaporator_in.y) annotation (Line(points={{52,
              -6},{60,-6},{60,-10},{69,-10}}, color={0,0,127}));
      annotation (
        Icon(coordinateSystem(preserveAspectRatio=false), graphics={
            Ellipse(lineColor = {75,138,73},
                    fillColor={255,255,255},
                    fillPattern = FillPattern.Solid,
                    extent={{-100,-100},{100,100}}),
            Polygon(lineColor = {0,0,255},
                    fillColor = {75,138,73},
                    pattern = LinePattern.None,
                    fillPattern = FillPattern.Solid,
                    points={{-36,60},{64,0},{-36,-60},{-36,60}})}),
        Diagram(coordinateSystem(preserveAspectRatio=false)),
        experiment(StopTime=900, __Dymola_Algorithm="Dassl"));
    end HeatPump_Test;

    annotation (
      Icon(
        graphics={
          Rectangle(
            lineColor={200,200,200},
            fillColor={248,248,248},
            fillPattern=FillPattern.HorizontalCylinder,
            extent={{-100,-100},{100,100}},
            radius=25),
          Polygon(
            origin={18,14},
            lineColor={78,138,73},
            fillColor={78,138,73},
            pattern=LinePattern.None,
            fillPattern=FillPattern.Solid,
            points={{-58.0,46.0},{42.0,-14.0},{-58.0,-74.0},{-58.0,46.0}}),
          Rectangle(
            extent={{-100,100},{100,-100}},
            lineColor={0,0,0},
            radius=25)}));
  end Examples;

  package FMI
    "Specifies models intended for export as FMU. The operation of the power-to-heat facility (heat pump and tank) is controlled via the external inputs (heat pump power consumption, tank dischargche mass flow)."

    model DHNetworkMassFlowControlled_FMU
      "This FMU exports the thermal system of the multi-energy network benchmark. The heating network is operated by directly controlling the mass flow, always providing enough to satisfy the demand of the consumers."
      Modelica.Blocks.Continuous.LimPID PID_controller(
        controllerType=Modelica.Blocks.Types.SimpleController.PID,
        k=1e-4,
        Ti=10,
        Td=10,
        yMax=5,
        yMin=0,
        withFeedForward=false)
        annotation (Placement(transformation(extent={{40,-70},{20,-90}})));
      Modelica.Blocks.Sources.Constant valve_grid_v1_setpoint(k=1) annotation (
          Placement(transformation(
            extent={{10,-10},{-10,10}},
            rotation=0,
            origin={-10,-80})));
      DHNetworkMassFlowControlled thermalNetwork(fileNameConsumer2=
            "modelica://ERIGridMultiEnergyBenchmark/data/heat_demand_load_profile_consumer1_1week.txt",
          fileNameConsumer1=
            "modelica://ERIGridMultiEnergyBenchmark/data/heat_demand_load_profile_consumer2_1week.txt")
        annotation (Placement(transformation(
            extent={{-30,-19},{30,19}},
            rotation=90,
            origin={-71,0})));
      Modelica.Blocks.Interfaces.RealInput mdot_tank_out
        "Setpoint for tank discharge mass flow in kg/s."
        annotation (Placement(transformation(extent={{140,-60},{100,-20}})));
      Modelica.Blocks.Interfaces.RealInput P_el_heatpump_setpoint_kW
        "Setpoint for heat pump power consumption in kW."
        annotation (Placement(transformation(extent={{140,-100},{100,-60}})));
      Modelica.Blocks.Interfaces.RealOutput T_tank_high_degC
        "Tank temperature in uppermost layer in °C."
        annotation (Placement(transformation(extent={{100,70},{120,90}})));
      Modelica.Blocks.Math.Gain P_el_heatpump_kW_to_W(k=1e3)
        annotation (Placement(transformation(extent={{80,-90},{60,-70}})));
      Modelica.Blocks.Interfaces.RealOutput T_tank_low_degC
        "Tank temperature in lowest layer in °C."
        annotation (Placement(transformation(extent={{100,30},{120,50}})));
      Modelica.Blocks.Math.Gain P_el_heatpump_W_to_MW(k=1e-6)
        annotation (Placement(transformation(extent={{60,-10},{80,10}})));
      Modelica.Blocks.Interfaces.RealOutput P_el_heatpump_MW
        "Heat pump power consumption in MW."
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      Modelica.Blocks.Math.UnitConversions.To_degC T_tank_high_to_degC
        annotation (Placement(transformation(extent={{60,70},{80,90}})));
      Modelica.Blocks.Math.UnitConversions.To_degC T_tank_low_to_degC
        annotation (Placement(transformation(extent={{60,30},{80,50}})));
    equation
      connect(valve_grid_v1_setpoint.y,thermalNetwork. valve_grid_v1_setpoint)
        annotation (Line(points={{-21,-80},{-30,-80},{-30,-25.2632},{-50.7333,
              -25.2632}},color={0,0,127}));
      connect(thermalNetwork.P_el_heatpump, PID_controller.u_m) annotation (
          Line(points={{-50.4167,4.73684},{30,4.73684},{30,-68}}, color={0,0,
              127}));
      connect(P_el_heatpump_setpoint_kW, P_el_heatpump_kW_to_W.u) annotation (
          Line(points={{120,-80},{82,-80}},color={0,0,127}));
      connect(PID_controller.u_s, P_el_heatpump_kW_to_W.y)
        annotation (Line(points={{42,-80},{59,-80}}, color={0,0,127}));
      connect(mdot_tank_out, thermalNetwork.mdot_tank_out) annotation (Line(
            points={{120,-40},{50,-40},{50,-6.31579},{-50.7333,-6.31579}},
            color={0,0,127}));
      connect(PID_controller.y, thermalNetwork.mdot_condenser_in) annotation (
          Line(points={{19,-80},{10,-80},{10,-15.7895},{-50.7333,-15.7895}},
            color={0,0,127}));
      connect(P_el_heatpump_W_to_MW.y, P_el_heatpump_MW)
        annotation (Line(points={{81,0},{110,0}}, color={0,0,127}));
      connect(P_el_heatpump_W_to_MW.u, thermalNetwork.P_el_heatpump)
        annotation (Line(points={{58,0},{30,0},{30,4.73684},{-50.4167,4.73684}},
            color={0,0,127}));
      connect(T_tank_high_degC, T_tank_high_to_degC.y)
        annotation (Line(points={{110,80},{81,80}}, color={0,0,127}));
      connect(T_tank_low_to_degC.u, thermalNetwork.T_tank_low) annotation (Line(
            points={{58,40},{40,40},{40,14.2105},{-50.4167,14.2105}}, color={0,
              0,127}));
      connect(T_tank_high_to_degC.u, thermalNetwork.T_tank_high) annotation (
          Line(points={{58,80},{20,80},{20,23.6842},{-50.4167,23.6842}}, color=
              {0,0,127}));
      connect(T_tank_low_to_degC.y, T_tank_low_degC)
        annotation (Line(points={{81,40},{110,40}}, color={0,0,127}));
      annotation (
        Icon(
          coordinateSystem(preserveAspectRatio=false),
          graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={227,221,16},
              fillPattern=FillPattern.Solid,
              radius=20),
            Text(
              extent={{-88,70},{90,-70}},
              lineColor={0,0,0},
              textString="m"),
            Ellipse(
              extent={{-6,50},{8,36}},
              pattern=LinePattern.None,
              lineColor={0,0,0},
              fillColor={0,0,0},
              fillPattern=FillPattern.Solid)}),
        Diagram(coordinateSystem(preserveAspectRatio=false)),
        experiment(StopTime=1, __Dymola_Algorithm="Dassl"),
        Documentation(info="<html>
    <p>This FMU exports the thermal system of the multi-energy network benchmark. The heating network is operated by directly controlling the mass flow, always providing enough to satisfy the demand of the consumers. The operation of the power-to-heat facility (heat pump and tank) is controlled via the external inputs (heat pump power consumption, tank dischargche mass flow).</p>
    </html>"));
    end DHNetworkMassFlowControlled_FMU;

    model DHNetworkPressureControlled_FMU
      "This FMU exports the thermal system of the multi-energy network benchmark. The heating network is operated by controlling the pressure, keeping the pressure drop at the consumers above a certain threshold."
      DHNetworkPressureControlled thermalNetwork(fileNameConsumer2=
            "modelica://ERIGridMultiEnergyBenchmark/data/heat_demand_load_profile_consumer1_1week.txt",
          fileNameConsumer1=
            "modelica://ERIGridMultiEnergyBenchmark/data/heat_demand_load_profile_consumer2_1week.txt")
        annotation (Placement(transformation(
            extent={{-30,-19},{30,19}},
            rotation=90,
            origin={-71,0})));
      Modelica.Blocks.Continuous.LimPID PID_controller(
        controllerType=Modelica.Blocks.Types.SimpleController.PID,
        k=1e-4,
        Ti=10,
        Td=10,
        yMax=5,
        yMin=0,
        withFeedForward=false)
        annotation (Placement(transformation(extent={{40,-70},{20,-90}})));
      Modelica.Blocks.Sources.Constant valve_grid_v1_setpoint(k=1) annotation (
          Placement(transformation(
            extent={{10,-10},{-10,10}},
            rotation=0,
            origin={-10,-80})));
      Modelica.Blocks.Math.Gain P_el_heatpump_kW_to_W(k=1e3)
        annotation (Placement(transformation(extent={{80,-90},{60,-70}})));
      Modelica.Blocks.Math.Gain P_el_heatpump_W_to_MW(k=1e-6)
        annotation (Placement(transformation(extent={{60,-10},{80,10}})));
      Modelica.Blocks.Interfaces.RealInput mdot_tank_out
        "Setpoint for tank discharge mass flow in kg/s."
        annotation (Placement(transformation(extent={{140,-60},{100,-20}})));
      Modelica.Blocks.Interfaces.RealInput P_el_heatpump_setpoint_kW
        "Setpoint for heat pump power consumption in kW."
        annotation (Placement(transformation(extent={{140,-100},{100,-60}})));
      Modelica.Blocks.Interfaces.RealOutput T_tank_high_degC
        "Tank temperature in uppermost layer in °C."
        annotation (Placement(transformation(extent={{100,70},{120,90}})));
      Modelica.Blocks.Interfaces.RealOutput T_tank_low_degC
        "Tank temperature in lowest layer in °C."
        annotation (Placement(transformation(extent={{100,30},{120,50}})));
      Modelica.Blocks.Interfaces.RealOutput P_el_heatpump_MW
        "Heat pump power consumption in MW."
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      Modelica.Blocks.Math.UnitConversions.To_degC T_tank_high_to_degC
        annotation (Placement(transformation(extent={{60,70},{80,90}})));
      Modelica.Blocks.Math.UnitConversions.To_degC T_tank_low_to_degC
        annotation (Placement(transformation(extent={{60,30},{80,50}})));
    equation
      connect(valve_grid_v1_setpoint.y,thermalNetwork. valve_grid_v1_setpoint)
        annotation (Line(points={{-21,-80},{-30,-80},{-30,-25.2632},{-50.7333,
              -25.2632}},color={0,0,127}));
      connect(thermalNetwork.P_el_heatpump, PID_controller.u_m) annotation (
          Line(points={{-50.4167,4.73684},{30,4.73684},{30,-68}}, color={0,0,
              127}));
      connect(P_el_heatpump_setpoint_kW,P_el_heatpump_kW_to_W. u) annotation (
          Line(points={{120,-80},{82,-80}},color={0,0,127}));
      connect(PID_controller.u_s, P_el_heatpump_kW_to_W.y)
        annotation (Line(points={{42,-80},{59,-80}}, color={0,0,127}));
      connect(mdot_tank_out, thermalNetwork.mdot_tank_out) annotation (Line(
            points={{120,-40},{50,-40},{50,-6.31579},{-50.7333,-6.31579}},
            color={0,0,127}));
      connect(PID_controller.y, thermalNetwork.mdot_condenser_in) annotation (
          Line(points={{19,-80},{10,-80},{10,-15.7895},{-50.7333,-15.7895}},
            color={0,0,127}));
      connect(P_el_heatpump_W_to_MW.y, P_el_heatpump_MW)
        annotation (Line(points={{81,0},{110,0}}, color={0,0,127}));
      connect(P_el_heatpump_W_to_MW.u, thermalNetwork.P_el_heatpump)
        annotation (Line(points={{58,0},{30,0},{30,4.73684},{-50.4167,4.73684}},
            color={0,0,127}));
      connect(T_tank_high_to_degC.y, T_tank_high_degC)
        annotation (Line(points={{81,80},{110,80}}, color={0,0,127}));
      connect(T_tank_low_to_degC.y, T_tank_low_degC)
        annotation (Line(points={{81,40},{110,40}}, color={0,0,127}));
      connect(T_tank_high_to_degC.u, thermalNetwork.T_tank_high) annotation (
          Line(points={{58,80},{20,80},{20,23.6842},{-50.4167,23.6842}}, color=
              {0,0,127}));
      connect(T_tank_low_to_degC.u, thermalNetwork.T_tank_low) annotation (Line(
            points={{58,40},{40,40},{40,14.2105},{-50.4167,14.2105}}, color={0,
              0,127}));
      annotation (
        Icon(
          coordinateSystem(preserveAspectRatio=false),
          graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={227,221,16},
              fillPattern=FillPattern.Solid,
              radius=20),
            Text(
              extent={{-88,70},{90,-70}},
              lineColor={0,0,0},
              textString="P")}),
        Diagram(coordinateSystem(preserveAspectRatio=false)),
        experiment(StopTime=1, __Dymola_Algorithm="Dassl"),
        Documentation(info="<html>
    <p>This FMU exports the thermal system of the multi-energy network benchmark. The heating network is operated by controlling the pressure, keeping the pressure drop at the consumers above a certain threshold.  The operation of the power-to-heat facility (heat pump and tank) is controlled via the external inputs (heat pump power consumption, tank dischargche mass flow).</p>
    </html>"));
    end DHNetworkPressureControlled_FMU;
    annotation (Icon(graphics={
          Rectangle(
            lineColor={200,200,200},
            fillColor={248,248,248},
            fillPattern=FillPattern.HorizontalCylinder,
            extent={{-100,-100},{100,100}},
            radius=25),                  Rectangle(
            extent={{-100,100},{100,-100}},
            lineColor={0,0,0},
            radius=25),
          Bitmap(extent={{-70,-62},{86,58}}, fileName=
                "modelica://ERIGridMultiEnergyBenchmark/images/fmi.svg")}));
  end FMI;
  annotation (uses(
      DisHeatLib(version="1.2"),
      IBPSA(version="3.0.0"),
      Modelica(version="3.2.3")));
end ERIGridMultiEnergyBenchmark;
