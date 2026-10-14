# Screen Reader Test Scripts

Skenario uji terstruktur untuk NVDA, VoiceOver, TalkBack. Gunakan per template dari `inventory/templates.md`.

---

## Setup Umum

### NVDA + Firefox/Chrome (Windows)
```
1. Install NVDA (nvaccess.org)
2. Buka browser, navigasi ke URL
3. NVDA+Space = Browse Mode ON
4. NVDA+F7 = Elements List (Headings, Links, Landmarks, Form Fields)
5. NVDA+F5 = Speech Viewer (log output)
6. NVDA+Ctrl+K = Keyboard Help (lihat command)
```

### VoiceOver + Safari (macOS)
```
1. Cmd+F5 = Toggle VoiceOver
2. Ctrl+Option+U = Rotor
3. Rotor > Headings / Links / Form Controls / Landmarks
4. Ctrl+Option+Left/Right = Navigate rotor items
5. Ctrl+Option+Space = Activate
6. VO Utility > Verbosity > Speech > "Speak hints" ON
```

### VoiceOver + Safari (iOS)
```
1. Settings > Accessibility > VoiceOver > ON
2. Rotor: Two-finger rotate > pilih Headings/Links/Forms
3. Swipe Right/Left = Next/Previous item
4. Double-tap = Activate
5. Three-finger swipe = Scroll
6. Settings > Accessibility > VoiceOver > Verbosity > Speak Hints ON
```

### TalkBack + Chrome (Android)
```
1. Settings > Accessibility > TalkBack > ON
2. TalkBack Menu: Three-finger tap OR Volume Up+Down (3x)
3. TalkBack Menu > Reading Controls > Headings/Links/Controls
4. Swipe Right/Left = Next/Previous
5. Double-tap = Activate
6. Two-finger swipe Up/Down = Scroll
```

---

## Skenario Uji Standar (Jalankan di Semua Template)

### S1: Page Orientation & Structure
```
ACTION: Load page, wait for full render
EXPECT: 
- Page title announced (2.4.2)
- Landmark regions announced: banner, navigation, main, contentinfo (1.3.1)
- Heading structure: h1 → h2 → h3... no skip levels (1.3.1)
- Main content reachable via Skip Link or Heading nav (2.4.1)
```

### S2: Keyboard Navigation Flow
```
ACTION: Tab through entire page (no mouse)
EXPECT:
- Focus visible on EVERY interactive element (2.4.7, 2.4.13)
- Focus order matches visual layout (2.4.3)
- No keyboard trap (2.1.2) - can Tab out of modals, menus, carousels
- Skip link works as first tab stop (2.4.1)
- Focus not obscured by sticky header/footer (2.4.11)
```

### S3: Heading Navigation (NVDA: H / Shift+H, VO: Rotor>Headings)
```
ACTION: Navigate by headings only
EXPECT:
- All content sections have descriptive headings
- Heading text matches visual heading
- No duplicate h1 (except maybe logo in banner)
- Hierarchy logical: h1 > h2 > h3...
```

### S4: Link Navigation (NVDA: K / Shift+K, VO: Rotor>Links)
```
ACTION: Navigate by links only
EXPECT:
- Link text describes destination/purpose (2.4.4)
- No "Click here", "Read more", "Link" as standalone text
- Same destination = same link text (consistent identification 3.2.4)
- External links indicated (icon + text "opens in new tab")
```

### S5: Form Field Navigation (NVDA: F / Shift+F, VO: Rotor>Form Controls)
```
ACTION: Navigate form fields only
EXPECT:
- Every input has accessible name (label, aria-label, title) (4.1.2)
- Required fields announced as "required" (3.3.2)
- Error messages announced on invalid submit (3.3.1, 4.1.3)
- Error suggestions announced (3.3.3)
- Autocomplete attributes correct (1.3.5)
- Label in Name: accessible name contains visible label (2.5.3)
```

### S6: Interactive Components
```
FOR EACH: Modal, Dropdown, Accordion, Tabs, Carousel, Menu
ACTION: Open, navigate, close via keyboard
EXPECT:
- Modal: Focus trapped, aria-modal="true", labelled (4.1.2)
- Dropdown: aria-expanded, aria-controls, Escape closes (4.1.2)
- Accordion: aria-expanded toggles, heading structure maintained
- Tabs: role=tablist/tab/tabpanel, arrow keys navigate, aria-selected (4.1.2)
- Carousel: Pause/Stop/Hide (2.2.2), keyboard nav prev/next
- Menu: role=menu/menuitem, arrow keys, Escape closes (4.1.2)
```

### S7: Dynamic Content & Live Regions
```
ACTION: Trigger updates (search, filter, add to cart, form error, toast)
EXPECT:
- Status changes announced via live region (4.1.3)
- aria-live="polite" for non-critical, "assertive" for errors
- No lost focus during update
- Loading states announced (aria-busy, aria-live)
```

### S8: Images & Non-Text Content
```
ACTION: Navigate to all images (NVDA: G, VO: Rotor>Images)
EXPECT:
- Informative images: alt text descriptive, concise (1.1.1)
- Decorative images: alt="" or role=presentation (1.1.1)
- Complex images (charts): long description available (1.1.1)
- Icons with text: icon hidden (aria-hidden), text visible
- Icon-only buttons: aria-label describes action
```

### S9: Tables
```
ACTION: Navigate table (NVDA: T, then Ctrl+Alt+Arrows)
EXPECT:
- Data tables: th with scope="col/row" (1.3.1)
- Table caption present (1.3.1)
- Header cells announced before data cells
- Layout tables: role=presentation OR no th
```

### S10: Multimedia
```
ACTION: Play video/audio
EXPECT:
- Video: Captions available, toggleable (1.2.2)
- Audio: Transcript link near player (1.2.1)
- Player controls keyboard accessible (4.1.2)
- Audio description track for video (1.2.3, 1.2.5)
- No auto-play audio > 3s without controls (1.4.2)
```

### S11: Zoom & Reflow (320px / 400%)
```
ACTION: Set viewport 320px wide OR browser zoom 400%
EXPECT:
- No horizontal scroll (1.4.10)
- Content reflows single column
- All functionality reachable
- Focus still visible
```

### S12: Text Spacing Override
```
ACTION: Apply user stylesheet (line-height 1.5, paragraph 2em, letter 0.12em, word 0.16em)
EXPECT:
- No content loss or overlap (1.4.12)
- All text readable
- Form fields still usable
```

---

## Per-Template Specific Scripts

### Template: Homepage
- [ ] Hero carousel: pause button, keyboard nav, live region for slide change
- [ ] Featured cards: heading structure, link purpose
- [ ] News feed: list markup, heading per item
- [ ] Footer: navigation landmarks, contact info

### Template: Berita/Artikel Detail
- [ ] Article heading h1, meta info (date, author) in header
- [ ] Body content: heading hierarchy, images with alt
- [ ] Related articles: list markup, link purpose
- [ ] Social share: button labels, keyboard accessible
- [ ] Comments form (if any): full form checklist

### Template: Kategori/Arsip
- [ ] Archive heading h1
- [ ] Article list: article>header>h2, excerpt, read more link
- [ ] Pagination: current page indicated, keyboard nav
- [ ] Filter/sort: form controls accessible, live region results

### Template: Program Detail
- [ ] Program header: h1, meta, featured image alt
- [ ] Tabs/sections: accessible tabs pattern
- [ ] Register/apply form: full form checklist
- [ ] Gallery: keyboard nav, alt text

### Template: Profil/About
- [ ] Section headings, team cards (name + role in heading)
- [ ] Org structure: list or table with headers
- [ ] Contact info: address, phone, email as links

### Template: Kontak
- [ ] Contact form: full form checklist (required, error, autocomplete)
- [ ] Map: iframe title, alternative text directions
- [ ] Office locations: list with headings
- [ ] Success/error message: live region

### Template: Pencarian
- [ ] Search input: label, autocomplete=off (or correct type)
- [ ] Results: heading "Search results for X", count announced
- [ ] Each result: heading link, snippet, URL
- [ ] No results: clear message, suggestions
- [ ] Pagination/facets: accessible

### Template: Error/404
- [ ] Clear heading "Page Not Found" (h1)
- [ ] Friendly message, not technical jargon
- [ ] Search link, home link, site map link
- [ ] Focus on heading on load

---

## Pencatatan Temuan

Format catatan per template per SR:

```
Template: [Nama Template]
SR: [NVDA/VoiceOver/TalkBack]
Browser: [Firefox/Chrome/Safari]
Date: YYYY-MM-DD
Tester: [Nama]

ISSUE-001:
- SC: 2.4.7 / 2.4.13
- Severity: Serious
- Element: [CSS selector atau description]
- Expected: Focus indicator visible
- Actual: No focus outline on button.primary
- Steps: Tab to button
- Recommendation: Add :focus-visible { outline: 3px solid #0066cc; }

ISSUE-002:
- SC: 1.1.1
- Severity: Moderate
- Element: Hero banner img
- Expected: Alt text describes image content
- Actual: alt="banner"
- Recommendation: alt="Inovasi OR.ID launches new accessibility initiative"
```

Masukkan ke `findings/findings.csv` dengan `source=manual`.

---

## Cross-SR Comparison Checklist

| Behavior | NVDA | VoiceOver macOS | VoiceOver iOS | TalkBack | Notes |
|----------|------|-----------------|---------------|----------|-------|
| Heading nav | H | Rotor>Headings | Rotor>Headings | Menu>Headings | |
| Link nav | K | Rotor>Links | Rotor>Links | Menu>Links | |
| Form nav | F | Rotor>Form Controls | Rotor>Forms | Menu>Controls | |
| Table nav | T + Ctrl+Alt+Arrows | Rotor>Tables | Rotor>Tables | Menu>Tables | |
| Live region | Auto | Auto | Auto | Auto | Test all 4 |
| Modal focus trap | ✓ | ✓ | ✓ | ✓ | Verify each |
| Aria-label reading | ✓ | ✓ | ✓ | ✓ | Verify each |

Catat perbedaan perilaku di `results/manual/sr-comparison-[YYYYMMDD].md`