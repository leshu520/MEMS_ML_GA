// this file includes Perface, Abbreviation Table, Contents, List of Figures
#import "@preview/acrostiche:0.3.2": *
#import "@preview/glossarium:0.4.1": print-glossary
= Perface
#line(length: 85%, stroke: 0.75pt)
#pagebreak()

#heading(level: 1)[Abbreviation Table]
#line(length: 85%, stroke: 0.75pt)
#print-glossary(
  (
    (
      key: "pem",
      short: "PEM",
      long: "Piezoelectric Materials",
    ),
    (
      key: "tia",
      short: "TIA",
      long:"Trans-Impedance Amplifier",
      desc:"A circuit that converts current to voltage.",
    ),
    (
      key: "fom",
      short: "FOM",
      long: "Figure of Merit",
    ),
    (
      key: "thd",
      short: "THD",
      long: "Total Harmonic Distortion",
      desc: "The ratio of the sum of the powers of all harmonic components to the power of the fundamental frequency.",
    ),
    (
      key: "comsol",
      short: "COMSOL",
      long: "COMSOL Multiphysics",
      desc: "A commercial software package developed by COMSOL Inc. for the modeling and simulation of any physics-based system.",
    ),
    (
      key: "fem",
      short: "FEM",
      long: "Finite Element Method",
      desc: "A numerical method for solving partial differential equations.",
    ),
    (
      key:"cpu",
      short: "CPU",
      long: "Central Processing Unit",
    ),
    (
      key: "pc",
      short: "PC", 
      long: "Personal Computer",
    ),
    (
      key: "aln",
      short: "AlN",
      long: "Aluminium Nitride", 
    ),
    (
      key: "spl",
      short: "SPL",
      long: "Sound Pressure Level",
    )
  ),
  disable-back-references: false
)
#pagebreak()

= Contents
#show outline.entry.where(
  level: 1
): it => {
  v(12pt, weak: true)
  strong(it)
}
#outline(title: none, indent: auto)

#pagebreak()
= List of Figures
#outline(title: none, target: figure.where(kind: image))
