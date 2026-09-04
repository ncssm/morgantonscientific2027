#set text(font: "Noto Sans", size: 10pt)

#let spacer = text(fill: gray)[ #h(8pt) | #h(8pt)]

#let papers = yaml("papers.yml")

#set page(
  paper: "us-letter",
  margin: (x: 3em, y: 5em),
  background: [
    #image("banner.jpg", width: 100%, height: 100%, fit: "cover")
  ],
  footer: text(fill: gray)[]
)

#align(center)[
  #grid(
    columns: (1fr, 1fr, 1fr),
    align(left, text(font: "Noto Serif", fill: white, size: 20pt)[2027]),
    [],
    align(right, text(font: "Noto Serif", fill: white, size: 20pt)[Volume 4])
  )
  #v(2em)
  #text(size:85pt, fill: white, font: "Noto Serif")[MORGANTON] \
  #text(size:102pt, fill: white, font: "Noto Serif")[SCIENTIFIC]
  #v(43em)
  #text(size:18pt, fill: white, font: "Noto Serif")[JOURNAL OF STUDENT STEM RESEARCH AT THE \
  NORTH CAROLINA SCHOOL OF SCIENCE AND MATHEMATICS]
]

#counter(page).update(0)

#pagebreak()

#set page(
  paper: "us-letter",
  footer: block(
    width: 100%,
    stroke: (top: 1pt + gray),
    inset: (top: 8pt, right: 2pt),
    context [
      Morganton Scientific | Volume 4 | 2026 - 2027
      #h(1fr)
      #counter(page).display()
    ]
  ),
  background: none,
)

#align(center)[
  #v(14em)
  #image("logo.png", width: 50%)
  #v(3em)
  #text(size:20pt, weight: "bold")[Morganton Scientific]
  #v(1em)
  #text(size:13pt)[North Carolina School of Science and Mathematics]
  #v(0.3em)
  #text(size:10pt)[Journal of Student STEM Research]
  #v(0.5em)
  #text(size:10pt, fill: black.lighten(40%), link("https://doi.org/[-doc.issue.doi-]")[https://doi.org/[-doc.issue.doi-]])
  #v(5em)
  #text(size:8pt, fill: black.lighten(40%), [Cover image by Layla Ibrahim])
]

#show heading: set text(fill: rgb("#C18849"))

#pagebreak()
= Table of Contents

#v(1em)
#{
  for paper in papers {
    block(
      breakable: false,
      [
        #if ("divider" not in paper) {
          table(
            columns: (35pt, auto),
            inset: 0em,
            stroke: none,
            gutter: 0em,
            [ #emph(str(paper.at("page")))], [ #text(size: 12pt, style: "italic", paper.at("title"))],
          )
          if ("author" in paper) {
            table(
              columns: (35pt, auto),
              inset: 0em,
              stroke: none,
              gutter: 0em,
              [], [ #text(size: 10pt, fill: black.lighten(20%), upper(paper.at("author")))]
            )
          }
        } else {
          table(
            columns: (35pt, auto),
            inset: 0em,
            stroke: none,
            gutter: 0em,
            [], [ #strong(text(size: 12pt, style: "normal", paper.at("title")))],
          )
        }
        #v(3pt)
      ]
    )
  }
}

#pagebreak()

[-CONTENT-]
