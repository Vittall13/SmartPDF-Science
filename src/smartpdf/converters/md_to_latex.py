"""Markdown to LaTeX converter."""
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MarkdownToLaTeX:
    """Convert Markdown to LaTeX document."""
    
    def __init__(self, document_class: str = "article"):
        self.document_class = document_class
    
    def convert(self, markdown_text: str, output_path: str | Path) -> None:
        """Convert Markdown to LaTeX.
        
        Args:
            markdown_text: Markdown text to convert
            output_path: Path to save .tex file
        """
        logger.info(f"Converting to LaTeX: {output_path}")
        
        # Start LaTeX document
        latex_lines = [
            f"\\documentclass{{{self.document_class}}}",
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage[russian,english]{babel}",
            "\\usepackage{amsmath}",
            "\\usepackage{amssymb}",
            "\\usepackage{graphicx}",
            "\\usepackage{booktabs}",
            "",
            "\\begin{document}",
            ""
        ]
        
        lines = markdown_text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip comments
            if line.startswith('<!--'):
                i += 1
                continue
            
            # Headers
            if line.startswith('#'):
                level = len(line.split()[0])
                text = line.lstrip('#').strip()
                
                if level == 1:
                    latex_lines.append(f"\\section{{{text}}}")
                elif level == 2:
                    latex_lines.append(f"\\subsection{{{text}}}")
                else:
                    latex_lines.append(f"\\subsubsection{{{text}}}")
            
            # Block formulas
            elif line.startswith('$$'):
                formula_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('$$'):
                    formula_lines.append(lines[i])
                    i += 1
                formula = '\n'.join(formula_lines)
                latex_lines.append("\\begin{equation}")
                latex_lines.append(formula)
                latex_lines.append("\\end{equation}")
            
            # Inline formulas
            elif '$' in line:
                # Convert inline formulas
                line = re.sub(r'\$([^$]+)\$', r'\\(\1\\)', line)
                latex_lines.append(line)
            
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                list_items = []
                while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                    list_items.append(lines[i].strip()[2:])
                    i += 1
                latex_lines.append("\\begin{itemize}")
                for item in list_items:
                    latex_lines.append(f"  \\item {item}")
                latex_lines.append("\\end{itemize}")
                continue
            
            # Tables
            elif line.startswith('|'):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i].strip())
                    i += 1
                self._add_table(latex_lines, table_lines)
                continue
            
            # Regular text
            elif line:
                latex_lines.append(line)
                latex_lines.append("")  # Empty line for paragraph break
            
            i += 1
        
        # End document
        latex_lines.append("")
        latex_lines.append("\\end{document}")
        
        # Save
        output_path = Path(output_path)
        output_path.write_text('\n'.join(latex_lines), encoding='utf-8')
        logger.info(f"LaTeX saved: {output_path}")
    
    def _add_table(self, latex_lines: list, table_lines: list) -> None:
        """Add table to LaTeX."""
        rows = []
        for line in table_lines:
            if '---' in line:
                continue
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            rows.append(cells)
        
        if not rows:
            return
        
        num_cols = len(rows[0])
        latex_lines.append("\\begin{table}[h]")
        latex_lines.append("\\centering")
        latex_lines.append(f"\\begin{{tabular}}{{{'c' * num_cols}}}")
        latex_lines.append("\\toprule")
        
        # Header
        latex_lines.append(" & ".join(rows[0]) + " \\\\")
        latex_lines.append("\\midrule")
        
        # Data rows
        for row in rows[1:]:
            latex_lines.append(" & ".join(row) + " \\\\")
        
        latex_lines.append("\\bottomrule")
        latex_lines.append("\\end{tabular}")
        latex_lines.append("\\end{table}")