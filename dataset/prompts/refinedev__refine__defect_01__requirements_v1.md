You are testing a deployed frontend implementation against the acceptance checklist below.

Use the browser like a black-box QA tester. Explore the relevant pages, interact with the UI, and use screenshots or video recordings when a requirement involves motion, timing, visual effects, input response, or multi-step state changes.

Check the checklist items one by one and determine how well the implementation satisfies them. Report your findings, including any unmet checklist items, the observed behavior, and concise evidence from your browser interactions.

Acceptance checklist:
## Public acceptance checklist

### R1 - Dashboard Data Modules and Date Filtering
When the user opens the Dashboard page, a card grid presents seven data modules: a Daily Revenue area chart, a Daily Orders bar chart, a New Customers bar chart, Delivery Map, Order Timeline, a Recent Orders table, and a Trending Products list. After the user opens the date-filter dropdown at the upper right and switches between Last Week and Last Month, the data areas in all chart modules refresh in sync. The x-axis date format automatically changes for the selected range: weekday abbreviations for the last seven days and MM/DD for the last month. The date and value shown in each chart's Tooltip remain consistent with the active filter range.

### R2 - Recent Orders Pending Actions and Data Synchronization
In the Dashboard's Recent Orders table, when the user opens the end-of-row action menu and clicks Accept for a Pending order, the order's status is updated to Ready. The system immediately shows a green success notification, removes that order's row from the current Pending list, decreases the total shown by the pagination controls in sync, and leaves no residual row for that order in the list. When the user clicks Reject, the order's status is updated to Cancelled, and the row is likewise removed immediately while the pagination total updates in sync. After either action, the list matches the server's current Pending state without requiring a page refresh or leaving and returning to Dashboard.

### R3 - Order List Status Chips and Action Buttons
On the Orders list page, the status column for every order is displayed as a Chip component. Pending has an orange border and a clock icon, Ready has a cyan border and a notification icon, On The Way has a blue border and a motorcycle icon, Delivered has a green border and a checkmark icon, and Cancelled has a red border and a cancel icon. After the user clicks Accept or Reject in the end-of-row action menu, the corresponding order's status Chip immediately changes to the new status color and icon, and the availability of the buttons in the action menu adjusts dynamically according to the order's current status.

### R4 - Order Details Status Actions and Button Availability
After the user clicks a row in the Orders list and enters the order details page, the page presents three areas: a Delivery Map, a product list, and Delivery Details. The Accept button at the top of the page is enabled only when the order's current status is Pending. The Reject button is enabled when the status is Pending, Ready, or On The Way. When the status is Delivered or Cancelled, both buttons are disabled. After the user clicks an enabled action button, the order status updates immediately, and the page's status Chip, button availability, and all related data refresh in sync without any inconsistent state.

### R5 - Delivery Map Markers and Interaction
When the user views the Dashboard's Delivery Map module or the delivery map on an order details page, the map uses Google Maps as its base map, with courier icons marking the delivery addresses of all orders whose status is On The Way and store icons marking their pickup addresses. After the user clicks any marker on the map, the system navigates to the corresponding order's details page and displays the order's complete information. When the map contains multiple markers, all markers are visible at the same time, and the map center and zoom level fit the full geographic distribution of the markers.

### R6 - Product List Dual-View Switching and Persistence
When the user switches between table view and card view with the ToggleButton on the Products list page, the page changes display modes immediately. Table view uses a DataGrid with columns for product ID, name, price, category, status, and other product data, while card view uses a grid of cards showing each product's thumbnail, name, price, and status label. The selected view mode is persisted to localStorage and automatically restored the next time the user enters the Products list page. Both views share the same pagination and filter criteria, and the current page and filtered results remain unchanged after the user switches views.

### R7 - Store List Dual-View Switching and Map Display
When the user switches between table view and map view with the ToggleButton on the Stores list page, the page changes display modes immediately. Table view uses a DataGrid with columns for store ID, name, email, phone number, status, and other store data, and supports pagination and filtering. Map view displays markers for the geographic locations of all stores on Google Maps; clicking any store marker navigates to that store's edit page. The selected view mode is persisted to localStorage. When the user switches views, the query parameters in the URL are cleared so that leftover parameters do not affect data loading in the new view.

### R8 - Grouped Global Search Autocomplete Results
After the user enters a keyword in the global search box in the top toolbar, the system searches orders, stores, and couriers in real time. Results appear in an Autocomplete dropdown grouped by resource type, and each option displays the corresponding resource's name and thumbnail. After the user clicks any search result, the system navigates to the corresponding resource's details page or edit page. An empty search box does not trigger a query. Whenever the input changes, the system issues a new query and replaces the previous results, keeping the dropdown data synchronized with the matches for the current keyword.

### R9 - Theme Switching and Internationalization
After the user clicks the theme toggle in the top toolbar, the color scheme of components throughout the system switches immediately between dark and light modes. The sidebar background, card backgrounds, text colors, chart colors, table-row backgrounds, and the theme colors of all Material UI components update in sync. After the user switches between English and German with the language dropdown, all interface copy immediately updates to the corresponding translation for the selected language, while the date formats and currency symbols in charts remain consistent with the language setting.

### R10 - Category Product Thumbnail Loading
When the user views category information on the Categories list page, the Products column in each category row displays a grid of thumbnail Avatar components for all products in that category. Each Avatar is 32x32 pixels, and hovering over it displays the corresponding product's full name in a Tooltip. While the product thumbnail data is loading, the column displays animated rectangular Skeleton placeholders; once loading finishes, the actual thumbnails replace the placeholders. The Categories list is not paginated, its bottom footer is hidden, and all categories are displayed at once.

### R11 - Multi-Step Courier Creation Form
After the user clicks Add new courier on the Couriers list page, the system opens a multi-step creation form with three steps: Personal, Company, and Vehicle. The user moves between steps with the Next and Prev buttons and can proceed to the next step only after all required fields in the current step pass validation. After the user submits the form, the system shows a success notification, the new courier appears immediately in the list, and the list's pagination total increases in sync.

### R12 - Order Timeline Pagination and Navigation
When the user views the order timeline in the Dashboard's Order Timeline module, the list shows recent orders in pages of 7. Each row displays an order-status Chip, the order number, and a relative time. After the user changes pages with the pagination controls at the bottom, the list immediately updates to the orders for the selected page, and the pagination control's current-page highlight updates in sync. After the user clicks any row in the timeline, the system navigates to the corresponding order's details page and displays the order's complete delivery information.
