#!/usr/bin/env Rscript

if (!nzchar(Sys.getenv("QUARTO_PROJECT_RENDER_ALL"))) {
  quit()
}

create_pub_listing <- function(bib_file, author = "Canouil") {
  bib <- strsplit(paste(readLines(bib_file), collapse = "\n"), "\n@")[[1]]
  articles <- lapply(
    X = paste0("@", bib[bib != ""]),
    FUN = function(ibib) {
      f <- tempfile()
      on.exit(unlink(f))
      writeLines(ibib, f)
      article <- tail(
        head(
          system(
            command = paste(
              "pandoc",
              f,
              "--standalone",
              "--from=bibtex",
              "--to=markdown"
            ),
            intern = TRUE
          ),
          -2
        ),
        -3
      )
      authors <- sub(
        ".*- family: ",
        "",
        grep("- family:", article, value = TRUE)
      )
      article <- c(
        article,
        sub(
          "  container-title: (.*)",
          "  journal-title: '*\\1*'",
          grep("  container-title:", article, value = TRUE)
        ),
        sub("  issued: ", "  date: ", grep("  issued:", article, value = TRUE)),
        sub(
          "  doi: ",
          "  path: https://doi.org/",
          grep("doi:", article, value = TRUE)
        )
      )
      article
    }
  )
  writeLines(text = unlist(articles), con = sub("\\.bib$", ".yml", bib_file))

  yaml_text <- c(
    "---",
    "title: 'Publications (%d)'",
    "title-block-banner: true",
    "image: /assets/images/social-profile.png",
    "date-format: 'MMMM,<br>YYYY'",
    "listing:",
    "  contents:",
    "    - publications.yml",
    "  page-size: 10",
    "  sort: 'issued desc'",
    "  type: table",
    "  categories: false",
    "  sort-ui: [date, title, journal-title]",
    "  filter-ui: [date, title, journal-title]",
    "  fields: [date, title, journal-title]",
    "  field-display-names:",
    "    date: Issued",
    "    journal-title: Journal",
    "---"
  )

  writeLines(
    text = sprintf(yaml_text, length(articles)),
    con = sub("\\.bib$", ".qmd", bib_file)
  )
}

create_pub_listing("publications.bib")
