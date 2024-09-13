===
1. Data model:
===

Here's a description of the key entities and their relationships:
Product
Represents the main items for sale (e.g., bicycles, potentially skis, surfboards in the future)
Fields: id, name, description, base_price
Relationships:
Many-to-many with Category
Many-to-many with Part
One-to-many with PriceRule
One-to-many with OrderItem
Category
Classifies products (e.g., Bicycles, Skis, Surfboards)
Fields: id, name
Relationships:
Many-to-many with Product
Part
Represents customizable components of a product (e.g., Frame, Wheels, Chain)
Fields: id, name, description
Relationships:
Many-to-many with Product
One-to-many with Option
Option
Specific choices for each Part (e.g., Full-suspension frame, Road wheels)
Fields: id, part_id, name, description, base_price, in_stock
Relationships:
Many-to-one with Part
Many-to-many with itself (for compatibility)
OptionCompatibility
Manages allowed combinations of options
Fields: option_id, compatible_option_id
This is a junction table for the self-referential many-to-many relationship in Option
PriceRule
Defines special pricing rules for option combinations
Fields: id, product_id, rule_type (e.g., "combination", "dependency"), price_adjustment
Relationships:
Many-to-one with Product
One-to-many with PriceRuleCondition
PriceRuleCondition
Specifies conditions for price rules
Fields: id, price_rule_id, part_id, option_id
Relationships:
Many-to-one with PriceRule
Many-to-one with Part
Many-to-one with Option
Order
Represents customer orders
Fields: id, customer_id, order_date, total_price
Relationships:
One-to-many with OrderItem
9. OrderItem
Individual items within an order
Fields: id, order_id, product_id, quantity, price, options (JSON field to store selected options)
Relationships:
Many-to-one with Order
Many-to-one with Product
This data model addresses the key requirements:
1. Product customization: The Part and Option entities allow for flexible product configuration.
Compatibility rules: The OptionCompatibility table ensures only valid combinations are allowed.
Dynamic pricing: PriceRule and PriceRuleCondition enable complex pricing logic based on selected options.
Inventory management: The 'in_stock' field in Option allows Marcus to mark items as out of stock.
Extensibility: The Category entity allows for easy addition of new product types beyond bicycles.

This model provides a robust foundation for Marcus's Bicycle Shop, allowing for complex product configurations, pricing strategies, and future expansion to other product types. It balances flexibility with structure, enabling the system to handle the intricate relationships between products, parts, and options while maintaining data integrity and supporting the required business logic.

===
2. Description of the main user actions:
===


## User Stories

### Roles

Two roles, owner of the shop (Owner), and Customer.

### Owner

* Selling Bicycles Online
As Owner,
I want to sell bicycles online through a website,
So that I can grow my business and reach more customers.

* Expand to Other Products
As Owner,
I want the website to be flexible enough to sell other sports-related items in the future (e.g., skis, surfboards, roller skates),
So that I can expand my product range as my business grows.

* Out of Stock Management
As Owner,
I want to mark certain part variations as "temporarily out of stock",
So that customers cannot order items that I cannot fulfill.

* Dynamic Price Adjustments
As Owner,
I want to apply dynamic pricing rules where certain part prices depend on other part selections (e.g., matte finish costs more on full suspension),
So that I don't lose money on customized bicycle orders.

* Admin: Manage Products
As Owner,
I want to create new products (e.g., new bicycle models or other sports-related items),
So that I can update my store's offerings.

* Admin: Manage Parts and Variations
As Owner,
I want to add or remove part choices (e.g., add new rim colors or remove discontinued ones),
So that I can keep my product catalog up-to-date.

* Admin: Update Pricing
As Owner,
I want to change prices for individual parts and configure special price rules for combinations (e.g., specific frame and finish combinations),
So that I can maintain flexible pricing for my products

### Customer

* Customizing Bicycles
As Customer,
I want to customize my bicycle by selecting different options for parts (e.g., frame type, wheel type, rim color, chain),
So that I can create a bicycle that fits my personal preferences and needs.

* Prohibited Combinations
As Customer,
I want to see which part combinations are not available based on my selections (e.g., mountain wheels only available with full suspension frames),
So that I avoid selecting incompatible bicycle parts.

* Viewing Available Options
As Customer,
I want to view available part options and prices for a specific bicycle model on the product page,
So that I can make informed decisions about my customization.

* Add Customized Bicycle to Cart
As Customer,
I want to add my customized bicycle to the shopping cart,
So that I can proceed to checkout and complete my purchase.

* Price Calculation for Bicycles
As Customer,
I want to see the total price of the customized bicycle,
So that I can understand how the price is derived from the selected parts.


===
3.
===

The product page is a crucial component of Marcus's Bicycle Shop, as it's where customers will customize their bicycles. Here's a detailed breakdown of how to implement this page:

UI Presentation:
1. Product Overview:
Display the product name, base description, and a default or configurable image.
Show the starting price (base price of the product).

2. Customization Section:
Organize customization options by part categories (e.g., Frame, Wheels, Chain).
For each part, present available options as radio buttons or dropdown menus.
Include brief descriptions and individual prices for each option.

Dynamic Visualization:
Implement a visual representation of the bicycle that updates as options are selected.
This could be done using layered images or a 3D model if feasible.

Price Summary:
Display a running total of the current configuration.
Break down the price by base price and additional costs for selected options.

5. Availability Indicator:
Clearly mark options that are out of stock.
6. Add to Cart Section:
Include an "Add to Cart" button.
Display the final price prominently.
Calculating Available Options:
1. Initial Load:
Fetch all parts and options associated with the product.
Check the 'in_stock' status for each option.
Dynamic Updates:
As the user selects an option for a part, query the OptionCompatibility table.
Disable or hide incompatible options for other parts.
Inventory Check:
Continuously check the 'in_stock' status of options.
Disable options that are out of stock.
Here's a pseudo-code representation of this process:

```python
def update_available_options(selected_options):
    for part in product.parts:
        for option in part.options:
            option.available = option.in_stock
            for selected_option in selected_options:
                if not are_options_compatible(option, selected_option):
                    option.available = False
                    break
    update_ui_with_available_options()
```


Price Calculation:
1. Base Price:
Start with the product's base price.
Option Prices:
Add the price of each selected option.
Price Rules:
Query the PriceRule and PriceRuleCondition tables for applicable rules.
Apply price adjustments based on the selected combination of options.
4. Dynamic Recalculation:
Recalculate the total price whenever an option is changed.
Here's a pseudo-code representation of the price calculation:
needed

```python
def calculate_total_price(product, selected_options):
    total_price = product.base_price
    for option in selected_options:
        total_price += option.price

    price_rules = get_applicable_price_rules(product, selected_options)
    for rule in price_rules:
        total_price = apply_price_rule(total_price, rule)

    return total_price

def apply_price_rule(current_price, rule):
    if rule.rule_type == 'fixed_adjustment':
        return current_price + rule.price_adjustment
    elif rule.rule_type == 'percentage_adjustment':
        return current_price * (1 + rule.price_adjustment / 100)
    # Add other rule types as needed
```

Implementation Details:

Use AJAX or a similar technology to update the UI dynamically without page reloads.
Implement client-side caching of compatibility rules and price calculations to reduce server load and improve responsiveness.
Use a state management solution (e.g., React's useState or Redux) to keep track of the current configuration.
Implement error handling to manage cases where selected options become incompatible or out of stock during the customization process.
Consider adding a "Reset to Default" button to allow users to start over easily.
Implement a "Save Configuration" feature for registered users, allowing them to save and return to custom builds.
This approach ensures a dynamic, responsive product page that handles the complex logic of bicycle customization while providing a smooth user experience. It accounts for the intricate relationships between parts and options, manages inventory constraints, and applies sophisticated pricing rules as required by Marcus's business model.

===
4.
===

When the customer clicks the "Add to Cart" button after customizing their product, several actions occur. Here's a detailed breakdown of what happens and what is persisted in the database:
1. Client-side validation:
Ensure all required options are selected.
Verify that the selected configuration is still valid (all parts are in stock and compatible).
Create a cart item:
If the user doesn't have an active cart, create one.
Generate a new cart item with the following information:
Product ID
Selected options for each part
Quantity (usually 1, unless the user specified otherwise)
Calculated price at the time of adding to cart
Send request to server:
Send an AJAX request to the server with the cart item details.
Server-side processing:
a. Validate the request:
Verify user session/authentication.
Re-check product availability and option compatibility.
Recalculate the price to ensure it matches the client-side calculation.
b. Database operations:
If no active cart exists for the user, create a new Cart entry.
Create a new CartItem entry with the following data:
;

```
        INSERT INTO CartItems (
          cart_id,
          product_id,
          quantity,
          price,
          options_json
        ) VALUES (
          :cart_id,
          :product_id,
          :quantity,
          :calculated_price,
          :options_json
        );
```

The options_json field stores a JSON representation of the selected options, e.g.:

```
        {
          "frame": {"id": 1, "name": "Full-suspension", "price": 130},
          "frame_finish": {"id": 5, "name": "Shiny", "price": 30},
          "wheels": {"id": 8, "name": "Road wheels", "price": 80},
          "rim_color": {"id": 12, "name": "Blue", "price": 20},
          "chain": {"id": 15, "name": "Single-speed chain", "price": 43}
        }
```
c. Update inventory (optional):
If you want to reserve inventory immediately, update the stock levels:
;

```
    UPDATE Options
    SET stock = stock - 1
    WHERE id IN (:selected_option_ids);
```

Note: This step is optional and depends on your inventory management strategy. Some systems only reduce stock at checkout.
d. Apply any relevant promotions or discounts.
Server response:
Send a success response back to the client, including:
Updated cart total (item count and price)
Confirmation of added item details
Client-side update:
Update the UI to reflect the new cart state (e.g., update cart icon, show confirmation message).
Optionally, display a mini-cart or cart summary.
(Optional) Persist cart for logged-in users:
If the user is logged in, you might want to persist their cart server-side so it's available across devices or sessions.
What is persisted in the database:
1. Cart table (if not already existing for the user):
;

```
   CREATE TABLE Carts (
     id INT PRIMARY KEY AUTO_INCREMENT,
     user_id INT,  -- NULL for guest users
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
   );
```

2. CartItem table:
;

```
   CREATE TABLE CartItems (
     id INT PRIMARY KEY AUTO_INCREMENT,
     cart_id INT,
     product_id INT,
     quantity INT,
     price DECIMAL(10, 2),
     options_json JSON,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
     FOREIGN KEY (cart_id) REFERENCES Carts(id),
     FOREIGN KEY (product_id) REFERENCES Products(id)
   );
```

Optional inventory update in the Options table.
Additional considerations:
1. Implement a mechanism to handle concurrent updates (e.g., using database transactions or optimistic locking).
Consider adding a time limit for cart items to manage abandoned carts.
3. Implement a strategy for merging carts when a guest user logs in or when accessing the cart from different devices.
Regularly clean up old or abandoned carts to manage database size.
By following this process, you ensure that the customer's customized product is accurately captured in the cart, the database reflects the current state of the user's selections, and the system is prepared for the eventual checkout process.


===
5.
===

The administration part of Marcus's Bicycle Shop website is crucial for managing the store's inventory, products, and pricing. Here are the main workflows for the administration interface:
Product Management
a. List Products:
Display a table of all products with basic information (name, category, base price, status).
Provide options to filter by category, search by name, and sort.
b. Add New Product:
Form to input basic product details (name, description, base price, category).
Option to associate parts that can be customized for this product.
Ability to set default options for each part.
c. Edit Existing Product:
Similar to the add form, but pre-populated with existing data.
Option to change product status (active/inactive).
d. Delete Product:
Soft delete to maintain order history integrity.
Part and Option Management
a. Manage Parts:
List all parts (e.g., frame, wheels, chain).
Add new parts or edit existing ones.
b. Manage Options for Each Part:
For each part, list available options.
Add new options with details (name, description, base price, initial stock).
Edit existing options (update price, description, stock levels).
Mark options as in stock or out of stock.
c. Option Compatibility:
Interface to set up compatibility rules between options.
Matrix or rule-based system to define which options can be combined.
Inventory Management
a. Stock Level Overview:
Dashboard showing current stock levels for all options.
Highlight low stock items.
b. Update Stock Levels:
Bulk update interface for quickly adjusting stock levels.
Option to set up low stock alerts.
c. Stock History:
View stock level changes over time.
Generate reports on popular items, frequent stockouts, etc.
Pricing Rules Management
a. List Pricing Rules:
Display all current pricing rules with their conditions and effects.
b. Create New Pricing Rule:
Form to define rule conditions (e.g., specific combination of options).
Set price adjustment (fixed amount or percentage).
Specify rule priority for cases where multiple rules might apply.
c. Edit Existing Rules:
Modify conditions, price adjustments, or rule priority.
d. Activate/Deactivate Rules:
Ability to temporarily disable rules without deleting them.
Order Management
a. Order List:
View all orders with basic information (order ID, customer, date, total, status).
Filter by date range, status, and search by order ID or customer name.
b. Order Details:
View complete order information including customer details, selected options for each product, pricing breakdown.
Option to update order status (e.g., processing, shipped, delivered).
c. Generate Reports:
Sales reports by product, category, or time period.
Customer purchase history and trends.
6. Customer Management
a. Customer List:
View all registered customers with basic information.
Search and filter capabilities.
b. Customer Details:
View individual customer's order history, saved configurations, etc.
Option to manage customer accounts (e.g., reset password, deactivate account).
Website Configuration
a. Category Management:
Add, edit, or remove product categories.
Arrange category display order.
b. Homepage Configuration:
Select featured products or categories for the homepage.
Update promotional banners or special offers.
c. Global Settings:
Set up tax rates, shipping methods and costs.
Configure payment gateways.
User Administration
a. Admin User Management:
Create, edit, or deactivate admin user accounts.
Assign roles and permissions to admin users.
b. Activity Logs:
View logs of admin actions for auditing purposes.
Implementation Considerations:
1. Use role-based access control to limit certain admin functions to specific user roles.
Implement confirmation dialogs for critical actions like deleting products or changing prices.
Use batch operations where possible for efficiency (e.g., updating multiple stock levels at once).
Provide a user-friendly interface for complex operations like setting up compatibility rules or pricing rules.
Implement robust error handling and validation to prevent data inconsistencies.
6. Use AJAX for real-time updates where appropriate to enhance user experience.
7. Ensure all admin actions are logged for accountability and troubleshooting.
By providing these administrative workflows, Marcus will have comprehensive control over his online store, allowing him to manage products, inventory, pricing, and orders efficiently. This system is flexible enough to accommodate future growth, such as adding new product types or implementing more complex pricing strategies.

===
6.
===

Creating a new product in Marcus's Bicycle Shop system involves collecting specific information and making several changes to the database. Let's break this down:
Information Required to Create a New Product:
Basic Product Information:
Product Name (e.g., "Mountain Explorer 2000")
Description
Base Price
Category (e.g., Mountain Bike, Road Bike)
SKU (Stock Keeping Unit)
Status (Active/Inactive)
Customizable Parts:
List of parts that can be customized for this product
Default option for each customizable part
Images:
Main product image
Additional images for different configurations
Inventory Information:
Initial stock level (if applicable for base product)
Low stock threshold
SEO Information:
Meta title
Meta description
URL slug
Related Products (optional):
IDs of related or complementary products
Database Changes After Creating a New Product:
When a new product is created, several tables in the database need to be updated:
Products Table:
;
ProductImages Table:
images
ProductParts Table (associating customizable parts with the product):
part
ProductDefaultOptions Table (setting default options for each part):
option
Inventory Table (if managing inventory at the product level):
;
RelatedProducts Table (if applicable):
product
Additional Considerations:
1. Transactions: Wrap all these insertions in a database transaction to ensure data integrity. If any insertion fails, the entire product creation should be rolled back.
Validation: Implement server-side validation to ensure all required fields are filled and data is in the correct format before attempting to create the product.
3. Unique Constraints: Ensure that unique fields like SKU and URL slug are indeed unique before insertion.
Logging: Log the product creation action in an admin activity log for auditing purposes.
Caching: If the application uses caching, invalidate or update relevant caches after adding the new product.
Search Index: If using a search engine like Elasticsearch, index the new product for search functionality.
Notifications: Potentially notify relevant staff or customers about the new product addition.
Pricing Rules: If there are any specific pricing rules for the new product, they should be set up in the PriceRules table.
9. Categories: Ensure the specified category exists before associating the product with it.
Options Compatibility: If the product has any specific compatibility rules between its customizable options, these should be set up in the OptionCompatibility table.
By following this process, Marcus can add new products to his store, complete with all the necessary information for customization, inventory management, and display on the e-commerce site. The database changes ensure that the new product is fully integrated into the existing system, maintaining the flexibility and functionality of the customization features.

===
7.
===

Certainly! Let's walk through the process of Marcus adding a new rim color to his bicycle customization options. We'll describe the UI for this action and the resulting database changes.
UI for Adding a New Part Choice:
Navigation:
Admin Dashboard > Parts Management > Wheels > Rim Colors
Rim Colors List View:
Display a table of existing rim colors with columns: Name, Description, Price Adjustment, Stock, Status (Active/Inactive)
Include an "Add New Rim Color" button at the top of the list
"Add New Rim Color" Form:
When Marcus clicks the "Add New Rim Color" button, a form appears with the following fields:
a. Name: Text input (e.g., "Metallic Green")
b. Description: Text area (e.g., "A vibrant metallic green finish")
c. Price Adjustment: Number input (e.g., 25.00)
d. Initial Stock: Number input (e.g., 100)
e. Status: Dropdown (Active/Inactive)
f. Compatibility:
Checkboxes or multi-select dropdown to choose compatible wheel types
This ensures the new color is only available for appropriate wheel options
g. Image Upload: File input to upload a sample image of the new color
h. Submit Button: "Add Rim Color"
Confirmation Dialog:
After submitting, show a confirmation dialog:
"Are you sure you want to add 'Metallic Green' as a new rim color option?"
[Cancel] [Confirm]
5. Success Notification:
Upon successful addition, display a success message:
"Metallic Green rim color has been added successfully!"
6. Return to List:
After adding, return to the updated Rim Colors List View with the new color included.
Database Changes:
When Marcus confirms the addition of the new rim color, the following changes occur in the database:
Update the Options table:
;
Update the OptionCompatibility table:
For each compatible wheel type selected, add an entry:
type
Optional: Update PriceRules table if there are any specific pricing rules for the new color:
options
Additional Considerations:
1. Validation: Implement server-side validation to ensure all required fields are filled and data types are correct.
2. Unique Constraints: Ensure that the combination of part_id and name in the Options table is unique to prevent duplicate entries.
Transaction: Wrap the database insertions in a transaction to ensure all related data is added successfully or rolled back if there's an error.
4. Caching: If the application uses caching for performance, invalidate or update relevant caches after adding the new option.
Logging: Log the action in an admin activity log for auditing purposes.
Inventory Alert: Set up a low stock alert for the new option if such a system is in place.
Product Updates: If any existing products use rim colors as a default option, provide a UI to update these products with the new color if desired.
By following this process, Marcus can easily add new rim colors (or any other part options) to his bicycle customization system. The UI provides a straightforward way to input the necessary information, while the database changes ensure that the new option is properly integrated into the existing product structure, maintaining data integrity and the flexibility of the customization system.

===
8.
===

Marcus needs a flexible system to manage pricing for individual parts and combinations of choices. Let's break down the UI and database changes for this pricing system:

UI for Price Management:
Main Pricing Dashboard:
Overview of current pricing rules
Options to manage individual part prices and combination prices
Individual Part Pricing:
a. List view of all parts and their options with current prices
b. "Edit" button next to each option
When Marcus clicks "Edit" for an option (e.g., diamond frame):
Pop-up form with fields:
Current base price
New base price
Effective date (optional, for scheduled price changes)
"Update Price" button
Combination Pricing Rules:
a. List of existing combination rules
b. "Add New Rule" button
When Marcus clicks "Add New Rule":
Form with the following elements:
Rule Name (e.g., "Premium Mountain Bike Setup")
Product dropdown (to associate the rule with a specific product type)
Dynamic selection of parts and options:
Dropdowns for each part category
Multi-select for options within each part
Price Adjustment:
Type: Radio buttons for "Fixed Amount" or "Percentage"
Value: Input field for the adjustment value
Priority: Number input (to handle conflicts between rules)
Start Date and End Date (optional, for time-limited rules)
"Save Rule" button
4. Edit Existing Rule:
Similar to the "Add New Rule" form, but pre-populated with existing data
"Update Rule" and "Delete Rule" buttons
Database Changes:
To accommodate this pricing system, we need to modify our database structure:
Update the Options table for individual part pricing:
;
Create a new table for combination pricing rules:
;
Now, let's look at how these database changes would be used:
Updating an individual part price:
;
Adding a new combination pricing rule:
;
Implementation Considerations:
Price Calculation Logic:
When calculating the final price of a customized product:
a. Start with the base product price
b. Add the base_price of each selected option
c. Apply any applicable combination rules, in order of priority
Caching:
Implement a caching system for pricing rules to avoid frequent database queries during price calculations.
3. Rule Conflicts:
Use the priority field to resolve conflicts when multiple rules could apply to the same combination.
Historical Pricing:
Consider implementing a system to track historical prices, which could be useful for order history and analytics.
Bulk Updates:
Provide a UI for bulk updating prices, especially useful for applying percentage increases across multiple parts or options.
Scheduled Updates:
Implement a job to apply scheduled price changes based on the price_effective_date.
Currency Handling:
If the shop operates in multiple currencies, ensure the system can handle currency conversions and display appropriate symbols.
Audit Trail:
Log all price changes for auditing purposes.
User Permissions:
Implement role-based access control to restrict price management to authorized personnel only.
Price Testing:
Consider adding a feature to test pricing rules on sample configurations before making them live.

This system provides Marcus with a flexible way to manage both individual part prices and complex pricing rules for combinations of options. The UI allows for easy management of these prices, while the database structure supports the storage and retrieval of this pricing information efficiently.
