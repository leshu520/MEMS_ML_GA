clc;
clear all;
% define global variables
% global ;
% GENERATIONS = ;
% POPULATIONSIZE = ;

%% define variable bounds for GA
[LowerBound,UpperBound] = UBLB_set();
%% GA function initialization 
% directly use the PyGAD module to enhance the model
% setup python (make sure your matlab link to Python interpreter)
% **note: check the campability of your MATLAB and Python
pyenv
pyModule = py.importlib.import_module('Genetic_algorithm.py');
pyModule = run_ga();

