# ETL-Copy

Repository to make modifications to ETL original project. Added more functionality to generate useful metadata for different configurations. 

1. Added pixel class and defined a new sensor in ETL.py to account for the pixel nature of the pixels in sensors. Code runs slow. The file pixel_testing.ipynb tests the functionality of these new classes by making plots and basic checks. 

2. To generate different configurations of moduels as per requirement, use make_txt2 function in generating txts.ipynb and define the modules to be removed and remove them from the output of the make_txt2 function. Saved the files in new_configs folder. 

3. To get the coorindates of the sensors in a yaml file, use the file realistic_layout_export.ipynb which reads in the txts generated and defines sensors for all the modules using make_modulefull function. 

4. Once you have the sensor yamls, run the simulation using different_configurations.ipynb and make calculations required. 

5. example.ipynb runs over an example which introduces the general structure of the code. filling original.ipynb fills some of the holes which can be filled with modules in the configurations and generates new txts.

6. SingleObjects.ipynb tests the functionality of the classes defined in ETL.py

