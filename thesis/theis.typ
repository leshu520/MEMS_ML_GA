// this is the main file for the thesis specially design for page setting 

#set page(number-align: right)
#set page(numbering: none)
#include("title.typ")
#pagebreak()

#set page(numbering:"I")
#counter(page).update(1)
#include("front_matter.typ")
#pagebreak()

#set page(numbering: "1")
#counter(page).update(1)
#include("chapter.typ")
#pagebreak()

#set page(numbering: "I")
#include("back_matter.typ")