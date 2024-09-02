
import markdown
import pypandoc
from tempfile import NamedTemporaryFile
import os

def save_as_word(text):

    def markdown_to_word(markdown_text, output_file):
            # Step 1: Convert Markdown to HTML
            html_text = markdown.markdown(markdown_text)
            
            # Step 2: Write HTML to a temporary file
            with NamedTemporaryFile('w', delete=False, suffix='.html') as temp_html_file:
                temp_html_file.write(html_text)
                temp_html_filename = temp_html_file.name
            
            try:
                # Step 3: Use pypandoc to convert HTML file to DOCX file
                pypandoc.convert_file(temp_html_filename, 'docx', outputfile=output_file)
            finally:
                # Clean up the temporary file
                os.remove(temp_html_filename)

    # Example markdown text
    markdown_text = text

    # Output Word document
    output_file = 'static/output.docx'

    # Convert markdown to word
    markdown_to_word(markdown_text, output_file)

    #print(f"Word document saved as '{output_file}'")
