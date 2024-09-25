===
1. Data model:
===

![Screenshot 2024-09-25 at 21 39 21](https://github.com/user-attachments/assets/9428237b-af85-4968-8970-bed034cf8ca0)

1. Products Table:

* Fields: id, name, description, base_price
* Represents the main products (e.g., bicycles, and potentially skis, surfboards, etc. in the future)

2. Categories Table:

* Fields: id, name
* Represents product categories (e.g., Bicycles, Skis, Surfboards)
* Relation: Many-to-Many with Products (through a junction table)

3. Parts Table:

* Fields: id, name, description, product_id
* Represents customizable parts of a product (e.g., Frame, Wheels, Chain)
* Relation: Many-to-One with Products

4. Options Table:

* Fields: id, name, description, price, part_id, in_stock
* Represents specific choices for each part (e.g., Full-suspension frame, Road wheels)
* Relation: Many-to-One with Parts

5. OptionCompatibility Table:

* Fields: id, option1_id, option2_id, compatible
* Represents compatibility between different options
* Relations: Two Many-to-One relationships with Options

6. PriceRules Table:

* Fields: id, name, price_adjustment, rule_type
* Represents special pricing rules for combinations of options
* Relation: Many-to-Many with Options (through PriceRuleConditions)

7. PriceRuleConditions Table:

* Fields: id, price_rule_id, option_id
* Junction table for PriceRules and Options
* Represents the conditions for each price rule

8. Orders Table:

* Fields: id, customer_id, order_date, total_price, product_id
* Represents customer orders
* Relations: Many-to-One with Products, Many-to-Many with Options

This data model allows for:
* Flexible product creation with customizable parts and options
* Managing option compatibility
* Complex pricing rules based on option combinations
* Inventory management (in_stock flag)
* Order tracking with selected options

The model is designed to be extensible, allowing Marcus to add new product types (like skis or surfboards) in the future without major structural changes.

===
2. Description of the main user actions:
===

Two users, Owner and Customer.

# TODO

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
3. The product page:
===

**How would you present the UI?**

As in Velodrom I would have a menu where I can select the different bike parts and would have a counter so you could get which parts are available or not while changing other parts. Only the available options for each part would be selected, and the others would be disabled with a meesage saying, "This option is not available for the selected parts".

**How would you calculate which options are available or not?**


I've implemented a set of rules (OptionCompatibility). These rules can be compatible and incompatible (bool) and are passed to a Feature model solver to get the available option, the current selected options and the newly calculated available options based on the selected options. Uses the Z3 python library. [The Z3 library is a theorem prover from Microsoft Research](https://github.com/Z3Prover/z3) and will return if the current set of logic predicates are satisfiable or not. The file implemented is `backend/app/services/selection_service.py`.


**How would you calculate the price depending on the customer's selections?**

For each option when the customer finishes the selection and on checktou the price is calculated in the folowing way.

For each option we check if there are PriceRules that affect the Option ID, if not we use the base price of the option.

If there are PriceRules that affect the Option ID, we calculate the price based on the rules, checking if the other option ids that are needed for the PriceRule are selected, if this is the case we apply the new price. You can see the implementation in the PriceService `backend/app/services/price_service.py`.


===
4.
===

When the customer clicks the "Add to Cart" button after customizing their product, several actions occur. Here's a detailed breakdown of what happens and what is persisted in the database:

I decided to have the order created the first time a Cutomer selects a option ("pending" status), so we could follow up the order if it's not completed with the customer if he/she has any issue and give us a phone/email. But we could persist the selectionin LocalStorage and create order only at the end on checkout. When the order is completed the order status is changed to "completed". We could have also "sent", or "payed" status if needed in the future.

We would need to have an order collector in the future for all those orders that are not completed, or change the order status to "cancelled" after a certain time of inactivity.

===
5. Description of the main workflows from the administration part of the website, where Marcus configures the store.
===

We need three main modules:

- Product creation module: Here we will be able to create a new product with its parts and the possible choices for each part.
- Choice Compatibility module: Here we will be able to modify the compatibity options a specific option has with others.
- Pricing module: Here we will be able to set the pricing rule (if any) for each option.

We will show if a specific option has compatibility rules and/or price rules in the overview of the product in the admin page.

===
6. The creation of a new product:
===

A new product needs to have, at least, a name and a description, a category, a part and an option for that part.

We will have:

- a new Product row
- a new Part row
- a new Option row

===
7. The addition of a new part choice:
===

He would go to the admin page, product view, then will go to the Rim part link and add a new option for that part, specifying the name, description and price. Then He could add a price rule for this option too if needed be.

===
8. Setting up prices:
===

He would go to the admin page, product view, then will go to the Frame part link and modify the base price for that part.

I He wants to set a specific price rule or rules for that part, he could add/ edit the ones that are already there, selecting the part and option related to the rule and then setting a price. He could do this several times if he wants more than one rule for this specific option.
