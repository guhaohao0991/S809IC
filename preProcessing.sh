#!/bin/bash

# Check if the OPENFOAM enviroment is set
if [ -z "$WM_PROJECT" ]; then
    echo "OpenFOAM environment not set"
    exit
fi

# Generate the airfoil mesh from coarse data points

echo "Generating airfoil mesh"
python genAirFoilMesh.py &> logMeshGeneration.txt
plot3dToFoam -noBlank volumeMesh.xyz >> logMeshGeneration.txt
autoPatch 45 -overwrite >> logMeshGeneration.txt
createPatch -overwrite >> logMeshGeneration.txt
renumberMesh -overwrite >> logMeshGeneration.txt
echo "Mesh generation completed!"
# copy initial conditions and boundary conditions to 0 folder
cp -r 0.orig 0

