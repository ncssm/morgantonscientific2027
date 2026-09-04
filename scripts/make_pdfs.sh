# Write initial papers.yml with no page numbers
bash ./generate_summary.sh ../templates/ncssm-preface/papers.yml 0 0 ../dividers/essays ../essays/* ../dividers/papers ../papers/*
# Generate frontmatter PDF (with invalid page numbers) to get it's page count
cd ../frontmatter
myst build --pdf
cd ../scripts
# Count the frontmatter pages
frontmatter_pages=$(pdftk ../frontmatter/article.pdf dump_data | grep NumberOfPages | awk '{print $2}')
if [ -z "$frontmatter_pages" ]; then
 echo "Error counting pages in ../frontmatter/article.pdf."
 exit 1
fi
# The cover page is unnumbered: templates/ncssm-preface/template.typ resets the
# page counter to 0 on it, so printed page numbers run one behind the physical
# page count. The last printed page of the frontmatter is the editors note, and
# the articles carry on from there.
editors_page=$((frontmatter_pages - 1))
# The foreword is the page before the editors note. Both are single pages; if
# either ever runs longer, these need recomputing rather than assuming.
foreword_page=$((frontmatter_pages - 2))
start_page=$frontmatter_pages
# Generate article PDFs with maybe wrong page numbers
for folder in $( ls -d -1 ../essays/* ../papers/* ../dividers/* ); do
 cd $folder
 myst build --pdf
 cd ../../scripts
done
# Update page numbers in article myst.ymls
bash ./update_pages.sh $start_page ../dividers/essays ../essays/* ../dividers/papers ../papers/*
# Re-generate PDFs with correct page numbers
for folder in $( ls -d -1 ../essays/* ../papers/* ../dividers/* ); do
 cd $folder
 myst build --pdf
 cd ../../scripts
done
# Write frontmatter page number summary, now that the articles are paginated
bash ./generate_summary.sh ../templates/ncssm-preface/papers.yml $foreword_page $editors_page ../dividers/essays ../essays/* ../dividers/papers ../papers/*
# Re-generate frontmatter PDF with the real page numbers
cd ../frontmatter
myst build --pdf
# Check the final frontmatter page count
final_frontmatter_pages=$(pdftk article.pdf dump_data | grep NumberOfPages | awk '{print $2}')
if [ "$final_frontmatter_pages" != "$frontmatter_pages" ]; then
 echo "Warning: frontmatter went from $frontmatter_pages to $final_frontmatter_pages pages once the page numbers were filled in."
 echo "Article page numbers are stale - re-run this script to settle them."
fi
cd ../
# Combine all PDFs into final PDF
pdftk frontmatter/article.pdf dividers/essays/divider.pdf essays/*/article.pdf dividers/papers/divider.pdf papers/*/article.pdf cat output morganton2027.pdf
