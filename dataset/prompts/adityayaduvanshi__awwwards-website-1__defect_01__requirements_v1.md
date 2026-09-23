You are testing a deployed frontend implementation against the acceptance checklist below.

Use the browser like a black-box QA tester. Explore the relevant pages, interact with the UI, and use screenshots or video recordings when a requirement involves motion, timing, visual effects, input response, or multi-step state changes.

Check the checklist items one by one and determine how well the implementation satisfies them. Report your findings, including any unmet checklist items, the observed behavior, and concise evidence from your browser interactions.

Acceptance checklist:
## Public acceptance checklist

### R1 - Hero Video and Erasable Canvas
After the user opens the home page, the FURROW header, menu button, red custom cursor, full-screen looping video, and the DIG DEEP title springing upward from below must be visible, while the canvas mask covers the video in the current theme color and retains the full viewport height. When the user presses the mouse button and moves across the hero canvas, the mask must be erased continuously along the pointer path with a thick stroke with rounded joins, revealing the underlying video. Erasing must stop when the user releases the mouse button, and the revealed areas must remain until the theme is switched or the window dimensions are recalculated, while the video continues playing at its original layer depth.

### R2 - Theme Switching and Local Persistence
When the user clicks the red dot in the middle of the FURROW logo, the page must switch between the dark and light themes, with the background, logo lettering, menu-button lines, body content, canvas mask, Services text, and footer icons all adopting the new theme colors in sync. After the user refreshes the page, it must load the last selected theme. The custom cursor must retain the red brand color and continue to follow the hover, locked, and nav-open state rules, and switching themes must not clear the page's current scroll position.

### R3 - Featured Project Card
When the user scrolls to the Featured Project section and hovers over the card, the PEI Seafood and 2023 metadata must fade in, the Not Humble title must remain at the bottom of the card, the right-pointing arrow must slide right from its left-side position, and featured-video.mp4 must continue playing muted on a loop in the background. When the user moves the pointer away, the metadata must fade out and the arrow must return to its starting point. The card height, title wrapping, and background-video crop must remain stable, and repeated hovers must not restart the entire page animation.

### R4 - Opening and Closing the Projects Panel
When the user clicks the menu button, the Projects panel must slide in from the left and cover the entire screen, with Projects and a close button at the top, five project entries in the middle, and an email address, phone number, and social icons at the bottom. The main page must retain its original scroll position, and clicks must not pass through the panel to it. After the user clicks the close button, the panel must slide out to the left without resetting the current theme, the hero's erasure marks, the custom cursor, or the Featured Project video state. When opened again, the panel must enter again as a red overlay.

### R5 - Project Hover Preview Mapping
With the Projects panel open, when the user hovers over NOT HUMBLE and 50 beaches in turn, the preview video on the right must map one-to-one to the currently hovered project title: NOT HUMBLE must use featured-video.mp4, matching the Not Humble Featured Project on the home page, while 50 beaches must use 50-beaches.mp4. When the user moves rapidly between the two rows, the current row's text and arrow must shift horizontally, the preview mask must reveal or conceal the video according to the current hover state, and the previous row's video must fade out without remaining under the new title.

### R6 - Switching Other Project Previews
When the user hovers in sequence over bleeping easy, make it zero, and it takes an island in the Projects panel, the preview area on the right must switch respectively to easy.mp4, make-it-zero.mp4, and it-takes-an-island.mp4, with the video fade-in and mask contraction occurring in sync. When the user moves the pointer off a project row, the mask must return to its covered state while the panel remains open. Hovering over the same project again must continue to show that project's corresponding media and must not be overridden by the home page's Featured Project video or the previous state of another project.

### R7 - Custom Cursor States
As the user moves the mouse across the page, the red circular cursor must follow the pageX/pageY coordinates without intercepting clicks. When it enters a standard clickable object, it must enlarge into the hollow hovered style; when it enters the menu button, it must lock near the button and display the locked style. After the user opens the Projects menu, the cursor must also adopt the nav-open state. Leaving a button, link, or social icon must restore the default circle, and moving rapidly across multiple objects must not leave multiple cursors or a mismatched border state.

### R8 - Services Accordion
When the user scrolls to the About and Services section, the About copy must first fade in from below, and the accordion must show the Pre-Production details by default. Clicking the Video Production, Post-Production, or Audio Post-Production title must expand or collapse the corresponding content area with a spring height transition. When the user hovers over a title, its text must change color according to the current theme, and the icon's two short lines must rotate according to the open and hover states. Expanded content must show only that group's service details and must not affect the footer or menu state.

### R9 - Footer Contact Details and Social Links
When the user scrolls to the bottom of the page, the footer must display a phone number, email address, postal address, and Instagram, Facebook, and Vimeo icons. The text and icon colors must inherit the current theme, and hovering over a social link must put the custom cursor into the hovered state. If the user opens the Projects panel while at the footer and then closes it, the footer must remain at its original scroll position, and its contact details must not be covered by the information at the bottom of the panel. After a theme switch, the footer icons and body copy must change color in sync.

### R10 - Responsive Layout and Media Placeholders
When the user changes the browser width or visits on a narrow-screen device, the hero video must continue to cover the viewport, the canvas dimensions must be recalculated, and the Projects panel, project list, right-side preview video, Services accordion, and footer contact details must remain within the readable area without causing horizontal page scrolling. While video resources are loading, the hero, Featured Project, and menu preview areas must retain their original heights. Once the resources finish loading, only the corresponding video image must update, without moving any title, button, or body copy already in the viewport or clearing the current theme.
