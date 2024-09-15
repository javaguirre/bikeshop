Bicycle Shop
You're tasked with building a website that allows Marcus, a bicycle shop owner, to sell his bicycles.



Marcus owns a growing business and now wants to sell via the internet. He also tells you that bicycles are his main product, but if the business continues to grow, he will surely start selling other sports-related items such as skis, surfboards, roller skates, etc. It would be a nice bonus if the same website allowed him to sell those things as well.



What makes Marcus's business successful is that customers can completely customize their bicycles. They can select many different options for the various parts of the bicycle. Here is an incomplete list of all the parts and their possible choices, to give an example:

Frame type: Full-suspension, diamond, step-through
Frame finish: Matte, shiny
Wheels: Road wheels, mountain wheels, fat bike wheels
Rim color: Red, black, blue
Chain: Single-speed chain, 8-speed chain


On top of that, Marcus points out that there are some combinations that are prohibited because they are not possible in reality. For example:

If you select "mountain wheels", then the only frame available is the full suspension.
If you select "fat bike wheels", then the red rim color is unavailable because the manufacturer doesn't provide it.


Also, sometimes Marcus doesn't have all the possible variations of each part in stock, so he also wants to be able to mark them as "temporarily out of stock" to avoid incoming orders that he would not be able to fulfill.



Finally, Marcus tells you how to calculate the price that you should present to the customer after the customization of the bicycle. Normally, this price is calculated by adding up the individual prices of each part that you selected. For example:

Full suspension = 130 EUR
Shiny frame = 30 EUR
Road wheels = 80 EUR
Rim color blue = 20 EUR
Chain: Single-speed chain = 43 EUR
Total price: 130 + 30 + 80 + 20 + 43 = 303 EUR

However, the price of some options might depend on others. For instance, the frame finish is applied at the end over the whole bicycle, so the more area to cover, the more expensive it gets. Because of that, the matte finish over a full-suspension frame costs 50 EUR, while applied over a diamond frame it costs 35 EUR.



These kinds of variations can always happen and they might depend on any of the other choices (not only two), so Marcus asks you to consider this because otherwise, he would be losing money.



This code exercise consists of defining a software architecture that could satisfy the requirements described above. In particular:

1 - Data model: What data model would be best to support this application? Could you describe it? Include table specifications (or documents if it's a non-relational database) with fields, their associations, and the meaning of each entity.

# TODO: Describe data model

2 - The description of the main user actions in this e-commerce website. Explain how they would work in detail.

3 - The product page: This would be a read operation, performed when you need to display the page of a product (a bicycle) for the customer to purchase. How would you present this UI? How would you calculate which options are available or not? How would you calculate the price depending on the customer's selections?

- Show the different parts of the bicycle and the possible choices for each part.
- When selecting an option on a part, the order will be updated and the available options will come from the calculation of the order and the price.
- The price of the order will be calculated based on the selected options and the pricing rules.
- The available options will be calculated based on the selected options and the availability/compatibility of the options.

4 - The "add to cart" action: Following the previous point, the product page should have a button to "add to cart" after the customer has made some specific selection. What happens when the customer clicks this button? What is persisted in the database?


- Based on the order information that we updated every time the order is updated, we will mark the order as "placed". The caveat is that we might be persisting orders than after will be discarded, but the good thing about this approach is that we could follow up the order if it's not completed with thecustomer if he/she has any issue and give us a phone/email.


5 - The description of the main workflows from the administration part of the website, where Marcus configures the store.

- We need three main modules:
  - Product creation module: Here we will be able to create a new product with its parts and the possible choices for each part.
  - Choice Compatibility module: Here we will be able to modify the compatibity options a specific option has with others.
  - Pricing module: Here we will be able to set the pricing rule (if any) for each option.

We will show if a specific option has compatibility rules and/or price rules in the overview of the product in the admin page.

6 - The creation of a new product: What information is required to create a new product? What changes in the database after performing this action?

A new product needs to have, at least, a name and a description, a category, a part and an option for that part.

We will have:

- a new Product row
- a new Part row
- a new Option row

# TODO How would we present this form??


7 - The addition of a new part choice: How can Marcus introduce a new rim color, for example? Can you describe the UI? What changes in the database after this action?

He would go to the admin page, product view, then will go to the Rim part link and add a new option for that part, specifying the name, description and price. Then He could add a price rule for this option too if needed be.

8 - Setting up prices: How can Marcus change the price of a specific part (like the diamond frame type) or specify that some combinations of choices have particular prices? How does the UI look? How does the database change to store this information?

He would go to the admin page, product view, then will go to the Frame part link and modify the base price for that part.

I He wants to set a specific price rule or rules for that part, he could add/ edit the ones that are already there, selecting the part and option related to the rule and then setting a price. He could do this several times if he wants more than one rule for this specific option.

---
