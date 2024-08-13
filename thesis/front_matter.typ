// this file includes Perface of the thesis

= Perface

#pagebreak()
// abbreviation table

= Contents
#show outline.entry.where(
  level: 1
): it => {
  v(12pt, weak: true)
  strong(it)
}
#outline(title: none, indent: auto) 
#pagebreak()

//#outline(title: "List of Figures", target: figure.where(kind: image))
//#outline(title: "List of Tables", target: figure.where(kind: table))