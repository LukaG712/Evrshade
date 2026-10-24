import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { remark } from 'remark'
import html from 'remark-html'
import gfm from 'remark-gfm'

const postsDirectory = path.join(process.cwd(), 'content/blog')

export function getPostSlugs() {
  return fs.readdirSync(postsDirectory)
}

export function getPostBySlug(slug: string) {
  const realSlug = slug.replace(/\.md$/, '')
  const fullPath = path.join(postsDirectory, `${realSlug}.md`)
  const fileContents = fs.readFileSync(fullPath, 'utf8')
  const matterResult = matter(fileContents)
  return {
    ...matterResult.data,
    slug: realSlug,
  }
}

export function getAllPosts() {
  const slugs = getPostSlugs()
  const posts = slugs
    .map((slug) => getPostBySlug(slug))
    .sort((a, b) => (a.date < b.date ? 1 : -1))
  return posts
}

export async function getPostData(slug: string) {
  const realSlug = slug.replace(/\.md$/, '')
  const fullPath = path.join(postsDirectory, `${realSlug}.md`)
  const fileContents = fs.readFileSync(fullPath, 'utf8')
  const matterResult = matter(fileContents)

  const processedContent = await remark()
    .use(gfm)
    .use(html)
    .process(matterResult.content)
  const contentHtml = processedContent.toString()

  // Extract headings for TOC
  const headings: { id: string; text: string; level: number }[] = []
  const headingRegex = /^(#{2,3})\s+(.+)$/gm
  let match: RegExpExecArray | null
  while ((match = headingRegex.exec(matterResult.content)) !== null) {
    const level = match[1].length // 2 for h2, 3 for h3
    const text = match[2].trim()
    const id = text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
    headings.push({ id, text, level })
  }

  return {
    slug: realSlug,
    contentHtml,
    headings,
    ...matterResult.data,
  }
}
