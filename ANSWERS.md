## 0. Introduction

I've decided to solve the problem using a relational database (PostgreSQL) and a Python/FastAPI backend. In the frontend I would go with Nextjs with a React framework.

I have a long experience using this stack and I believe is the best stack for me to deliver a working solution in a reasonable time with a good architecture. I also think if this is a somewhat realistic scenario for a real case, this stack would be a good choice.

Frontend and Backend would connect through an HTTP API, using JSON format for the data and JWT for the authentication. The frontend would control the session using the JWT through a cookie. We would separate authorization depending on the role (admin or customer) and the actions in the API. If needed we would store some temporal information in LocalStorage, always checking with backend for critical actions.

## 1. Data model:

![Screenshot 2024-09-25 at 21 39 21](https://github.com/user-attachments/assets/9428237b-af85-4968-8970-bed034cf8ca0)

1. Products Table:

* Fields: id, name, description, base_price
* Represents the main products (e.g., types of bicycles (MTB, Racing), and potentially types of skis, surfboards, etc. in the future)

2. Categories Table:

* Fields: id, name
* Represents product categories (e.g., Bicycles, Skis, Surfboards)
* Relation: Many-to-Many with Products (through a junction table)

3. Parts Table:

* Fields: id, name, description, product_id
* Represents customizable parts of a product (e.g., Frame, Wheels, Chain in case of a bike)
* Relation: Many-to-One with Products

4. Options Table:

* Fields: id, name, description, price, part_id, in_stock
* Represents specific choices for each part (e.g., Full-suspension frame, Road wheels...), With the in_stock flag we could manage the stock of each option and if it's in_stock or not to filter out the options.
* Relation: Many-to-One with Parts

5. OptionCompatibility Table:

* Fields: id, option1_id, option2_id, compatible
* Represents compatibility between different options, it can be compatible or incompatible (bool)
* Relations: Two Many-to-One relationships with Options

6. PriceRules Table:

* Fields: id, name, price_adjustment, rule_type
* Represents special pricing rules for combinations of options, depending on the price rule condition, the price for the calculation will be price_adjustment or the price from the option
* Relation: Many-to-Many with Options (through PriceRuleConditions)

7. PriceRuleConditions Table:

* Fields: id, price_rule_id, option_id
* Junction table for PriceRules and Options
* Represents the conditions for each price rule

8. Orders Table:

* Fields: id, customer_id, order_date, total_price, product_id
* Represents customer orders, and the options selected for that order
* Relations: Many-to-One with Products, Many-to-Many with Options

This data model allows for:
* Flexible product creation with customizable parts and options
* Managing option compatibility
* Complex pricing rules based on option combinations
* Inventory management (in_stock flag)
* Order tracking with selected options

The model is designed to be extensible, allowing Marcus to add new product types (like skis or surfboards) in the future without major structural changes.

## 2. Description of the main user actions:

Two users, Owner and Customer. Not clear which would be the "main" user, so I'll put here the main actions for each user.

### Owner

The Owner will be able to create new products with its category, parts and options (see UI below).

He will also be able to modify the compatibility of the options using the compatibility flag to fine tune the options, and the pricing rules for each option in the admin page.

### Customer

The Customer will be able to select the parts and options for the product and add it to the cart.

He will be able to browse through the homepage to see the different products, products we have featured.

He could browse through a category page to see the products in that category.

Once He/She has selected the product, he will be able to see the different parts and options for that product and start configuring the product.

When selecting an option for a part, the customer will be able to see some options are available, some are not, depending on their selection. They could also see the price for the option selected and the total price for the product.

After selecting all the parts for the product, the customer will be able to see the total final price for the product and add it to the cart. The customer will be able to see the total price for the product every time he/she selects an option for a part, but only when all parts are selected will be able to finish the order, which is "pending" since the moment they select the first option until they complete the order.

On the cart page, the customer will be able to see the products added to the cart and the total price for each product and the final price, and they could complete the order and pay for it.

## 3. The product page:

**How would you present the UI?**

Similar to Velodrom, I would have a menu where I can select the different bike parts and would have a facet for the options per part so you could get which parts are available or not while changing other part options. Only the available options for each part would be available, and the others would be disabled with a meesage saying, "This option is not available for the selected parts". We don't have pictures now, but eventually we would so the customer knows which option he/she is selecting better.

![Screenshot 2024-09-25 at 21 47 46](https://github.com/user-attachments/assets/a74ab779-1e1a-48d3-8378-d082c59fd017)

**How would you calculate which options are available or not?**

I've implemented a set of rules (OptionCompatibility). These rules can be compatible or incompatible (bool) and are passed to a Feature model solver to get the available option, the current selected options and the newly calculated available options based on the selected options. Uses the Z3 python library. [The Z3 library is a theorem prover from Microsoft Research](https://github.com/Z3Prover/z3) and will return if the current set of logic predicates are satisfiable or not. The file implemented is `backend/app/services/selection_service.py`.

The implementation makes easy to add new rules and automated testing, easy to scale in the future.

**How would you calculate the price depending on the customer's selections?**

For each option when the customer finishes the selection and on checkout the price is calculated in the following way:

- For each option we check if there are PriceRules that affect the Option ID, if not we use the base price of the option.

- If there are PriceRules that affect the Option ID, we calculate the price based on the rules, checking if the other option ids that are needed for the PriceRule are selected, if this is the case we apply the new price. You can see the implementation in the PriceService `backend/app/services/price_service.py`.


## 4. The "add to cart" action:

When the customer clicks the "Add to Cart" button after customizing their product, several actions occur. Here's a detailed breakdown of what happens and what is persisted in the database:

The frontend will send a PUT request to the backend with the changed status of the order. At this point the backend will check if the final selection is correct and will calculate the price again to check if there is any mismatch (This is not implemented yet).

If there is any problems, we will return a 400 status and the error message to the frontend.

In case everything is 200 OK:

I decided to have the order created the first time a Customer selects an option when customizing the product ("pending" status), so we could follow up the order if it's not completed with the customer if he/she has any issue and give us a phone/email. We could persist the selection in their browsers LocalStorage and create order only at the end on checkout too, but I believe this is more realistic in terms of a real case scenario.

When the order is completed the order status is changed to "completed". We could have also "sent", or "payed" status if needed in the future.

This order is changed in the database and could trigger other processes, for example, sending an email to the customer with the order details.

We would need to have an order collector (e.g: a periodic background task) in the future for all those orders that are not completed, or change the order status to "cancelled" after a certain time of inactivity.

## 5. Description of the main workflows from the administration part of the website, where Marcus configures the store.

We need three main modules:

- Product creation module: Here we will be able to create a new product with its parts and the possible choices for each part.
- Choice Compatibility module: Here we will be able to modify the compatibity options a specific option has with others.
- Pricing module: Here we will be able to set the pricing rules (if any) for each option. Right now only the first rule matching is selecting for a specific option, but we could improve this by using the Z3 solver to select the best rule (the one that will give the highest discount) considering the other options selected (for example).

We will show if a specific option has compatibility rules and/or price rules in the overview of the product in the admin page.

## 6. The creation of a new product:

UI With all the possible fields for the product.

![Screenshot 2024-09-26 at 20 44 04](https://github.com/user-attachments/assets/f46e62bb-1042-43ca-a6bb-536f8fa387ab)

UI without the rules and compatibility options, Option Compatibility and Price Rules are collapsed.

![Screenshot 2024-09-26 at 20 44 09](https://github.com/user-attachments/assets/bd0b08bb-78c5-4709-ab5a-759b6f771e3f)

A new product needs to have, at least, a name and a description, a category, a part and an option for that part.

First we will submit the product form with the basic product information. This will be a POST request to the /products endpoint.

Once this happens, if everything is 201 OK, we will have a new Product row in the database and will be redirected to the next step, the part form.

Here we will have a master detail view, with the list of parts for that product in the master view and the options for the selected part in the detail view. If there aren't any we will show the part creation view form.

When we submit the part form, (only a name and an optional description for now), we will POST to the /parts endpoint and update the master part list view with the new part.

If we select an existing part, the options list will appear with the options for that part. Here we could create a new one having the form for the option with the part_id already set and filling the name, base price and description. This will be a POST request to the /options endpoint and the new option will be added to the list.

After these first steps are done, we could set price rules and compatibility rules for the options if needed.


## 7. The addition of a new part choice:

![Screenshot 2024-09-26 at 20 45 26](https://github.com/user-attachments/assets/c29dbdfa-7a39-4d17-9f6a-3e52e767ea33)

Marcus would go to the admin page, products view. Select a product and then the Parts/Options master detail view will show.

He would select a part, then in the options he would click the "Add" button to add a new option. An inline form will appear and Marcus will be able to fill the name, description and base price for the new option.

Once the option is created, Marcus will be able to add a price rule/compatibility rule for that option if needed.

## 8. Setting up prices:

![Screenshot 2024-09-26 at 20 35 35](https://github.com/user-attachments/assets/ecc19f4d-12ec-40db-9247-2bc0810e8d16)

Every option will have an input field on creation/update. If a price rule is needed for a specific part and option, we would fill a form such as the screenshot, where we could add/remove options and set the adjusted price.

When clicking the "Save" button, a POST or PUT (create or update) request will be sent to the backend and if the validation is OK, the PriceRule row will be created and the PriceRuleCondition row for each option and price rule.

In the future we would implement the delete button for the price rules.
