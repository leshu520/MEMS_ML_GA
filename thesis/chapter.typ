//formula use all uppercase letter
#import "@preview/mitex:0.2.4": *
#import "@preview/glossarium:0.4.1": make-glossary,gls,glspl
#show: make-glossary
#set heading(numbering: "1.1.1.")
#set math.equation(numbering: "(1)")
#set par (justify: true)
    
= Introduction
Speaker and microphone are widely used in our daily life...  
= Theoretical Background
== Polarization
Electric field is able to polarized dielectric material. There are several polarization in the material, they are electronic polarization, ionic polarization, and orientation polarization respectively. @ionic-polarization demonstrates the net polarization happens when exerting an external electric field, the positive charge and negative charge will flow to opposite direction of the field @RN18. With the polarization, the internal charge balanced distribution will be disrupted, leading to the generation of the current. 
#figure(
  image("ionic-polarization.svg", width: 65%),
  caption: [
    The effect of an external electric field on an ionic material. 
  ],
)<ionic-polarization>

== Piezoelectricity
=== Crystal structure
@pem are materials that can generate an net polarization internally in response to an applied mechanical stress. Without the applied stress, the material is in a neutral state. While the stress applied to the crystal of centra-symmetric materials, the unit cell becomes strained. However, the center of mass of the negative charge still coincides with the positive charge so that results in a zero net polarization meaning this crystal structure is not capable for the @pem. The @pem is always non-centra-symmetric. When stress applied, the center of the mass for the positive and negative charges will displace, result in a net polarization difference showed in @non-centro-crystal @RN21. 

#figure(
  image("non-centra-symmetry.png", width: 70%),
  caption: [
    a) The crystal structure of non-centro-symmetric material. b) The net polarization when stress applied on vertical direction. c) The net polarization when stress applied on horizontal direction.
  ],
)<non-centro-crystal>
=== Piezoelectric effect <piezo-effect-section>
The piezoelectricity can be understood as a linear electromechanical interaction between the mechanical and electrical polarization. The linearity relationship could be characterized by following equation, 

$ P_i = d_(i j) T_j $<coefficient>

Here, $T_j$ is the stress along $j$ direction and $P_i$ is the polarization intensity along $i$ direction which is the sum of electric dipole moments per unit volume. The $d_(i j)$ is the piezoelectric coefficient and this is a constant specific for each @pem. Air propagates from the top to the bottom, exerting pressure perpendicular to the @pem, making charge to be generated in the horizontal direction. 
#parbreak()
The piezoelectric effect is reversible, meaning that the material can also deform when an electric field is applied. 
=== Electrical displacement and Charge
// Take reference from the paper
=== Sensing
The polarization generates the charge difference and transmit to the electrode from @pem. The charge will generate current since 
$ I = (dif Q)/(dif t) $ <equationI>
where $I$ is the current, $Q$ is the charge with the time $t$. However, the current is not able to be processed by the downstream circuit. The current can to be converted to voltage via @tia. In this project, we don't consider about the external circuit design for the sensor, just by the assumption that the @tia is ideal and perfectly matched with it. 
== Aluminium Nitride
The material used here is @aln, which is a type of widely used piezoelectric material. 
== Figure of Merit of Microphone
From the relationship from @piezo-effect-section, microphone is based on the stress applied on the @pem, and the speaker is based on the electric field applied on the @pem. In this project, we only focus on the microphone. 
=== Frequency response 
The @fom is a parameter that is used to evaluate the performance of the microphone. More charge is generate, the more sensitivity the microphone has. 
//take reference from some textbooks
Also the flatness of the electricity response given by the microphone is another important parameter, avoiding the potential distortion of the sound. For these sound frequency that has low response in the electrical field, the microphone will have a low sensitivity. To compensate for this, the filter will be introduced for the system. However, this also amplifies low-response frequency, leading to amplification of the noise. Thus, the @thd increases lead to the sensitivity decreasing. 

According to @equationI, high frequency component has lower $t$ in respect of charge. Therefore,  the low-frequency response is another a @fom for the microphone indicates the bottleneck of the microphone's ability to generate signal. While low-frequency signals are crucial as they capture the depth and warmth of sounds, which are essential for producing rich and full audio experiences. Nowadays, the capability for microphone to extend to lower frequency is one of a important #glspl("fom"). 
=== Capture ability 
For a microphone, basically the structure is a membrane anchored on the frame with electrode surrounding. The charge is able to flow into the electrode and connect with external circuit. The capability of a microphone to capture given @spl need to be deduced. The equations is given by the following analysis. 

Since the piezoelectricity is a linear relationship with the stress applied on the @pem, we can focus on the total force that given by the sound wave. The total stress can be written as @total-stress,
$ F_j = integral.triple_cal(V)S_j dif x dif y dif z $ <total-stress>
supposed $j$ is the direction of the stress, $S_j$ is the stress applied on the PEM at every position, and $A$ is area of the @pem. The total force is the integration of the force applied on the PEM. //need to extend from here

To direct evaluate the performance, alternatively, we can use total charge. The total charge by the piezoelectric membrane generated can be written as @total-charge, 
$ Q = integral.triple_cal(V) sigma dif V $ <total-charge>
while the $sigma$ is the charge density on the @pem. The total charge is the integration of the charge density by the whole PEM zone. @total-charge circumstances the analysis of the solid mechanics, forwarding to the final optimization target. 

Because for the numerical analysis, only formula expressed discrete form is acceptable. Rewrite the @total-charge as following,  

$ Q approx sum_i sigma_i Delta V_i $

where the $V_i$ is the size of the volume element $i$, and $sigma_i$ is the charge density of the corresponding volume element $i$. In the discrete formulation, the calculation accuracy is determined by the size of $Delta V$.
 
The microphone has different response according to different frequency, measuring single frequency is very inaccurate. Thus, we could consider the frequency could be heard by human, which is from 20~Hz -- 20~kHz. The charge from  @total-charge need to be integral over the frequency range. The FOM can be written by the following equation, 
$ "FOM"=integral_(20)^(20000) Q_p dif f $<FOM>
where $p$ is the index of the frequency. 

@FOM is also able to expressed in a discrete form, but it's more complicated than previous derivation. First we need to define the step of each frequency,
$ Delta f = (20000-20)/N $ <frequency_step_1>
Then, adapt the formula into discrete frequency $f_i$, 
$ f_i = 20 + (i - 1)Delta f, quad "for " i=1,2,3 dots ,N $ <frequency_step_2>
Bring @frequency_step_1 and @frequency_step_2 into @FOM, 
$ "FOM" approx sum_(i=1)^N Q_p (f_i) Delta f $
This is similar to the previous derivation, the accuracy of the calculation is determined by the size of $Delta f$.

== Genetic algorithm <section-genetic>
The optimization of genetic algorithm is inspired by the Darwin's 
=== Mutation 
Mutation is a important factor that bring the diversity for 
== Concurrent system <section-concurrent>
Modern computers are equipped with sophisticated scheduling systems that distribute workloads evenly across each core of the @pc. However, these systems often fall short when managing dedicated tasks, resulting in suboptimal efficiency. To address this issue, it is essential to incorporate principles and methodologies of concurrent system design. This approach will enhance task-specific scheduling performance, ensuring more effective achievement of desired outcomes. 
=== Threading


== Parametric curvature <section-parametric>

= Integration
@comsol is the a software based on simulation, which is widely used in the industry. The software based on the @fem solver to solve the partial differential equation. However, this method has 
As mentioned in the @section-genetic, genetic algorithm is a widely used method to solve optimization problem. There is lot of open-source library that can be used to save the time for developing own genetic function, PYGAD is one of them. With the assistance of the MPH library, PYGAD can manipulate the @comsol model and automatically obtain the result. After iterations, the optimal result can be obtained.
== Computation timing optimization

// not finished yet, gonna to add it later
= 2D model<chapter-2Dmodel>
== COMSOL model
//The 2D model is built in the @comsol,
= 3D Model
== Simplification of the model
After converting from 2D to 3D model, the computational requirements for simulating the model have significantly increased, leading to a corresponding increase in the time needed to obtain FOM. To reduce the computational requirements, the model has to be simplified. 
=== Symmetry
The membrane of my microphone is circular, making it easy to divide into two, four, or eight equal parts. The geometry design on each segment can be duplicated across the others, resulting in identical simulation outcomes for each section. With the decrease of area applied on mesh operation, the accuracy of the final result will increase for the same mesh granularity. 

However, the free geometry design is about destroying the symmetry of the model inherently. This method has constrain on cutting the membrane method. The number of the segments need to be considered accordingly. 
=== Mesh operation
The mesh operation gives us a way to solve the @fem problem numerically, properly setting the mesh is crucial. 

The free tetrahedral mesh is the default mesh operation in the @comsol, which is the most accurate mesh operation. However, the computational requirement is also the highest. Since we are not exploring on the very high accuracy to perceive the distortion occurred in the model, the free Tetrahedral mesh is not necessary. 



=== Use stress as FOM

== Simulation Setup

