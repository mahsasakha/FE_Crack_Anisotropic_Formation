# FE_Crack_Anisotropic_Formation

This repository contains Python code and APDL scripts for running ANSYS APDL simulations and performing subsequent analysis. The code is designed to simulate the behavior of an infinite transversely isotropic formation under in-situ compressive loading with a circular hole under pressure, extracting the stress distribution (hoop stress) around the hole. Additionally, the code considers different material orientations to analyze the effects of anisotropy on stress distribution.

Overview of Simulations and Analysis
1- APDL.txt: This script performs the following steps:

Models an infinite transversely isotropic formation.
Applies in-situ compressive loading.
Creates a circular hole under pressure, with the pressure value based on calculations.
Extracts the stress distribution (hoop stress) around the hole.
Varies the material orientation multiple times and stores hoop stress data for each orientation in different CSV files.

Based on the calculations of the APDL.txt, the python code determines the point (distance from the hole and orientation with respect to the horizon) where the strength-based criterion is met.

2- APDL_Crack_Wellbore.txt: After identifying the point where the strength-based criterion is met in the previous simulation, this script performs the following:

Forms a crack with the crack tip located at the identified point.
Calculates the strain energy density between two states: crack-free and cracked.

Based on the calculations of the APDL_Crack_Wellbore.txt, the python code computes the energy release rate between these two states.
it then compares the calculated energy release rate with the critical energy release rate to determine if the fracture energy criterion is met.


Prerequisites
Before using this code, ensure you have the following:

ANSYS installed on your system.
Python installed with necessary libraries (NumPy, Pandas, etc.) specified in requirements.txt.
Usage
Clone this repository to your local machine:

bash
Copy code
git clone https://github.com/your-username/your-repo.git
Install the required Python libraries:

bash
Copy code
pip install -r requirements.txt
Modify the APDL.txt and APDL_Crack_Wellbore.txt scripts as needed to specify simulation parameters and material properties.

Run the Python code to automate ANSYS APDL simulations and analysis:

bash
Copy code
python run_ansys.py
Results
After running the code, you will obtain the following:

CSV files containing hoop stress data for different material orientations.
Information about the point where the strength-based criterion is met.
Analysis results indicating whether the fracture energy criterion is met.
License
This code is provided under the MIT License.

Acknowledgments
If you use this code in your research or project, please consider citing the authors or providing an acknowledgment.
