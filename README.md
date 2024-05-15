# Turbocase

Making a nice case for a PCB project is not terribly hard, but it is annoyingly time consuming if you just want a
simple functional case. This most of the time for a case design for me is spend on figuring out how to align the
mounting holes in the PCB with the 3D print and ensure the cutouts for the connectors are correct.

This project provides a ~~hacky~~ neat way to generate an OpenSCAD project based on the data in a KiCAD PCB file.

To define the shape of the case create a drawing of inside edge of the case on one of the user layers. This follows
the same semantics as the PCB fabrication outline on the Edge.Cuts layer. By default turbocase reads the outline from
the User.6 layer.

Turbocase will automatically extract information about MountingHole footprints and place plastic posts underneath the
PCB to fit threaded metal inserts after 3D printing. It currently is hardcoded to the bag of M3 inserts I have.

For connectors KiCAD needs to learn about the third dimension. For this purpose I have added a "Height" property to
the connects I want to be processed by turbocase that defines the height from the top of the PCB to the top of the
connector so an appropiate cutout can be made in the case. The rest of the shape of the connector is defined by the
bounding box of the F.Fab layer of the connector.

## Installation

```shell-session
$ pip install turbocase
```

## Usage

```shell-session
$ turbocase project/project.kicad_pcb case.scad
```