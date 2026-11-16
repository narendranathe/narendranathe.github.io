"""Contracts for the studio reading path, replacing retired homepage components.

The old impact strips, hover previews, skills tooltips and format-switching hero
picture are no longer on this homepage. Their old component tests remain in
test-portfolio.py for the older layout. Sitewide claim, identity, asset, link,
sitemap and copy guards still run for the new design.
"""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
RETIRED_COMPONENT_TESTS = {
    'test_styles_css_has_impact_strip_module', 'test_hero_uses_local_photo_not_external_cdn',
    'test_hero_aside_no_data_reveal', 'test_hero_picture_has_mobile_variant',
    'test_hero_preload_uses_imagesrcset', 'test_hero_picture_has_avif_and_webp_variants',
    'test_jetbrains_mono_loaded', 'test_css_uses_tabular_nums', 'test_css_has_print_block',
    'test_data_reveal_reduced_motion_fallback', 'test_css_mobile_breakpoint_at_600px',
    'test_css_uses_warm_palette_tokens', 'test_hover_preview_css_module_present',
    'test_hover_preview_resume_triggers_count', 'test_hover_preview_contact_icons_annotated',
    'test_hover_preview_total_triggers_count', 'test_hover_preview_every_linkedin_link_annotated',
    'test_hover_preview_linkedin_trigger_count', 'test_hover_preview_substack_trigger_count',
    'test_hover_preview_resume_cache_bust_matches_sidecar', 'test_substack_triggers_have_embed_attrs',
    'test_styles_css_has_feed_list_module', 'test_skills_tooltip_suppression_css_rule_present',
    'test_hero_picture_breakpoint_matches_layout', 'test_hero_img_has_width_and_height',
    'test_hero_img_has_lcp_attributes', 'test_hero_alt_text_includes_role',
    'test_systems_table_reflows_on_narrow_screens',
}

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tags=[]; self.ids=[]; self.buttons=[]; self.stack=[]; self.words=[]
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs);self.tags.append((tag,a))
        if a.get('id'):self.ids.append(a['id'])
        if tag=='button':self.buttons.append(a)
        if tag not in ('meta','link','br','img','input','hr','source','wbr','path','circle','ellipse','rect'):
            self.stack.append(tag)
    def handle_endtag(self,tag):
        if tag in self.stack:
            i=len(self.stack)-1-self.stack[::-1].index(tag);self.stack=self.stack[:i]
    def handle_data(self,data):
        if any(t in self.stack for t in ('head','style','script','title','desc')):return
        if 'details' in self.stack and 'summary' not in self.stack:return
        self.words.extend(data.split())

def test_studio_homepage_reading_budget():
    page=Page((ROOT/'index.html').read_text())
    assert 450<=len(page.words)<=650, f'{len(page.words)} visible words; expected 450-650'

def test_studio_work_precedes_biography():
    ids=Page((ROOT/'index.html').read_text()).ids
    expected=['hero','systems','projects','decisions','about','contact']
    positions=[ids.index(item) for item in expected]
    assert positions==sorted(positions)

def test_studio_portrait_is_local_and_immediately_visible():
    text=(ROOT/'index.html').read_text()
    image=next(a for t,a in Page(text).tags if t=='img' and 'headshot' in a.get('src',''))
    assert (ROOT/image['src']).is_file()
    assert image.get('width')=='800' and image.get('height')=='1000'
    assert image.get('fetchpriority')=='high' and image.get('loading')=='eager'
    assert 'Naren' in image.get('alt','') and 'Data Engineer' in image.get('alt','')
    assert 'data-reveal' not in text

def test_studio_figures_have_accessible_names():
    for filename in ['index.html','database-refresh.html','repo-context-hooks.html','fraud-detection.html']:
        for tag,attrs in Page((ROOT/filename).read_text()).tags:
            if tag=='svg' and attrs.get('aria-hidden')!='true':
                assert attrs.get('role')=='img', filename
                assert attrs.get('aria-label') or attrs.get('aria-labelledby'), filename

def test_studio_refresh_stages_and_default_explanation():
    for filename in ['index.html','database-refresh.html']:
        page=Page((ROOT/filename).read_text())
        stages=[a for a in page.buttons if 'data-step' in a]
        assert [a['data-step'] for a in stages]==['restore','security','recovery','cdc','listener']
        assert sum(a.get('aria-pressed')=='true' for a in stages)==1
        assert {a['data-refresh-mode'] for a in page.buttons if 'data-refresh-mode' in a}=={'manual','automated'}

def test_studio_case_studies_explain_different_systems():
    expected={'database-refresh.html':'data-refresh-demo','repo-context-hooks.html':'data-context-demo','fraud-detection.html':'data-replay-demo'}
    for name,marker in expected.items():
        text=(ROOT/name).read_text()
        assert marker in text and 'decision-grid' in text
        assert len([1 for t,a in Page(text).tags if t=='h1'])==1
        assert 'class="case-note"' in text and '<details' in text

def test_studio_demos_are_labeled_and_controls_use_native_buttons():
    context=(ROOT/'repo-context-hooks.html').read_text()
    fraud=(ROOT/'fraud-detection.html').read_text()
    assert 'frontend explanation' in context and 'Frontend simulation' in fraud
    assert 'not a live agent session' in context and 'No model or database runs' in fraud
    for name in ['index.html','database-refresh.html','repo-context-hooks.html','fraud-detection.html']:
        for button in Page((ROOT/name).read_text()).buttons:
            assert button.get('type')=='button', name
            if any(k in button for k in ['data-step','data-refresh-mode','data-context']):
                assert button.get('aria-pressed') in ['true','false'], name

def test_studio_resume_links_keep_the_current_binary_hash():
    text=(ROOT/'index.html').read_text()
    links=[a['href'] for t,a in Page(text).tags if t=='a' and 'resume.pdf' in a.get('href','')]
    assert len(links)>=3 and all('v=b0a4215e' in url for url in links)

def test_studio_reduced_motion_and_focus_have_rules():
    css=(ROOT/'studio.css').read_text()
    assert '@media(prefers-reduced-motion:reduce)' in css and 'scroll-behavior:auto' in css
    assert ':focus-visible' in css and 'outline:3px' in css
    assert not re.search(r'opacity:\s*0(?:[;}])',css), 'Content must not wait for animation/JS'
    assert '@media(max-width:600px)' in css and '.workflow-track{grid-template-columns:1fr' in css

def test_studio_scripts_do_not_call_production_services():
    js=(ROOT/'studio.js').read_text()
    assert 'textContent' in js and 'addEventListener' in js
    assert not any(value in js for value in ['fetch(', 'XMLHttpRequest', 'innerHTML', 'eval('])
    assert 'arrivals += 1' in js and 'Stored predictions: 1.' in js

STUDIO_TESTS=[test_studio_homepage_reading_budget,test_studio_work_precedes_biography,
test_studio_portrait_is_local_and_immediately_visible,test_studio_figures_have_accessible_names,
test_studio_refresh_stages_and_default_explanation,test_studio_case_studies_explain_different_systems,
test_studio_demos_are_labeled_and_controls_use_native_buttons,test_studio_resume_links_keep_the_current_binary_hash,
test_studio_reduced_motion_and_focus_have_rules,test_studio_scripts_do_not_call_production_services]
