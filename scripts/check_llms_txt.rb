#!/usr/bin/env ruby
# frozen_string_literal: true

require "pathname"
require "set"
require "yaml"

class LLMSTxtChecker
  REPO_ROOT = Pathname(__dir__).join("..").expand_path
  LLMSTXT_PATH = REPO_ROOT.join("llms.txt")
  CONFIG_PATH = REPO_ROOT.join("scripts", "llms_guardrails.yml")
  RAW_PREFIX = "https://raw.githubusercontent.com/datacommonsorg/docsite/master/"

  Doc = Struct.new(
    :path,
    :title,
    :llms_mode,
    :layout,
    :published,
    :content,
    keyword_init: true
  )

  def run
    docs = load_docs
    linked_paths = extract_linked_paths
    errors = []

    errors.concat(invalid_mode_errors(docs))
    errors.concat(link_errors(docs, linked_paths))
    errors.concat(missing_coverage_errors(docs, linked_paths))

    if errors.empty?
      puts "llms.txt guardrail passed."
      puts "Eligible docs: #{eligible_docs(docs).length}"
      puts "Linked raw repo docs: #{linked_paths.length}"
      return
    end

    $stderr.puts "llms.txt guardrail failed:"
    errors.each do |error|
      $stderr.puts "- #{error}"
    end
    exit 1
  end

  private

  def load_docs
    docs = []
    markdown_paths.each do |relative_path|
      next if excluded_path?(relative_path)

      docs << build_doc(relative_path)
    end
    docs
  end

  def markdown_paths
    Dir.chdir(REPO_ROOT) { Dir.glob("**/*.md").sort }
  end

  def excluded_path?(relative_path)
    return true if ignored_files.include?(relative_path)
    return true if excluded_prefixes.any? { |prefix| relative_path.start_with?(prefix) }
    return true if relative_path.split("/").any? { |segment| segment.start_with?("_") }

    filename = File.basename(relative_path)
    filename.start_with?("_")
  end

  def build_doc(relative_path)
    content = REPO_ROOT.join(relative_path).read
    front_matter_text, body = split_front_matter(content)
    front_matter = front_matter_text ? (YAML.safe_load(front_matter_text, aliases: true) || {}) : {}

    Doc.new(
      path: relative_path,
      title: front_matter["title"]&.to_s&.strip,
      llms_mode: front_matter["llms"]&.to_s&.strip,
      layout: front_matter["layout"]&.to_s&.strip,
      published: front_matter["published"],
      content: body || content
    )
  end

  def split_front_matter(content)
    match = content.match(/\A-{3,}\s*\r?\n(.*?)\r?\n-{3,}\s*\r?\n?(.*)\z/m)
    return [nil, content] unless match

    [match[1], match[2]]
  end

  def extract_linked_paths
    raise "Missing llms.txt at #{LLMSTXT_PATH}" unless LLMSTXT_PATH.exist?

    text = LLMSTXT_PATH.read
    text.scan(%r{#{Regexp.escape(RAW_PREFIX)}([^\s)]+\.md)}).flatten.map do |path|
      path
    end
  end

  def invalid_mode_errors(docs)
    docs.each_with_object([]) do |doc, errors|
      next if doc.llms_mode.nil? || doc.llms_mode.empty?
      next if %w[ignore include].include?(doc.llms_mode)

      errors << "#{doc.path} has invalid llms value #{doc.llms_mode.inspect}; use 'ignore' or 'include'."
    end
  end

  def link_errors(docs, linked_paths)
    docs_by_path = docs.each_with_object({}) { |doc, memo| memo[doc.path] = doc }

    linked_paths.each_with_object([]) do |path, errors|
      doc = docs_by_path[path]
      if doc.nil?
        errors << "llms.txt references missing docs path #{path}."
      elsif hard_exclusion_reason(doc)
        errors << "llms.txt references excluded page #{path} (#{hard_exclusion_reason(doc)})."
      elsif forbidden_reason(doc)
        errors << "llms.txt references forbidden page #{path} (#{forbidden_reason(doc)})."
      end
    end
  end

  def missing_coverage_errors(docs, linked_paths)
    linked_set = linked_paths.to_set

    eligible_docs(docs).each_with_object([]) do |doc, errors|
      next if linked_set.include?(doc.path)

      errors << "Eligible page #{doc.path} is missing from llms.txt. Suggested entry: #{suggested_entry(doc)}"
    end
  end

  def eligible_docs(docs)
    docs.reject do |doc|
      hard_exclusion_reason(doc) || forbidden_reason(doc) || invalid_llms_mode?(doc)
    end
  end

  def invalid_llms_mode?(doc)
    mode = doc.llms_mode
    return false if mode.nil? || mode.empty?

    !%w[ignore include].include?(mode)
  end

  def hard_exclusion_reason(doc)
    return "empty file" if doc.content.to_s.strip.empty?
    return "layout: redirect" if doc.layout == "redirect"
    return "layout: code-preview" if doc.layout == "code-preview"
    return "published: false" if doc.published == false

    nil
  end

  def forbidden_reason(doc)
    return "front matter llms: ignore" if doc.llms_mode == "ignore"

    ignored_prefix = ignored_prefixes.find { |prefix| doc.path.start_with?(prefix) }
    return nil if ignored_prefix.nil?
    return nil if doc.llms_mode == "include"

    "ignored prefix #{ignored_prefix.inspect}"
  end

  def ignored_prefixes
    @ignored_prefixes ||= begin
      prefixes = llms_guardrails["ignored_prefixes"] || []
      unless prefixes.is_a?(Array) && prefixes.all? { |prefix| prefix.is_a?(String) }
        raise "scripts/llms_guardrails.yml must define ignored_prefixes as an array of strings."
      end

      prefixes
    end
  end

  def excluded_prefixes
    @excluded_prefixes ||= begin
      prefixes = llms_guardrails["excluded_prefixes"] || []
      unless prefixes.is_a?(Array) && prefixes.all? { |prefix| prefix.is_a?(String) }
        raise "scripts/llms_guardrails.yml must define excluded_prefixes as an array of strings."
      end

      prefixes
    end
  end

  def ignored_files
    @ignored_files ||= begin
      files = llms_guardrails["ignored_files"] || []
      unless files.is_a?(Array) && files.all? { |file| file.is_a?(String) }
        raise "scripts/llms_guardrails.yml must define ignored_files as an array of strings."
      end

      files
    end
  end

  def llms_guardrails
    @llms_guardrails ||= CONFIG_PATH.exist? ? (YAML.safe_load(CONFIG_PATH.read, aliases: true) || {}) : {}
  end

  def suggested_entry(doc)
    display_title = doc.title.nil? || doc.title.empty? ? File.basename(doc.path, ".md") : doc.title
    "- [#{display_title}](#{RAW_PREFIX}#{doc.path}): TODO add routing note."
  end
end

LLMSTxtChecker.new.run
