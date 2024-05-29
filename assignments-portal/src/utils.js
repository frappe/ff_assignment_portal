import markdownit from 'markdown-it'

const md = markdownit();

export function md2html(markdown) {
    return md.render(markdown);
}
