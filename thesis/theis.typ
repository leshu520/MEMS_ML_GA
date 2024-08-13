#set page(numbering: none)
#include("title.typ")

#set page(numbering:"i", number-align: right)

#counter(page).update(1)
#include("front_matter.typ")

#set page(numbering:"1", number-align: right)
#counter(page).update(1)
#include("chapter.typ")