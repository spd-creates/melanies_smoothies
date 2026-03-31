# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col ###    use snowpark
import requests  # python library

# Write directly to the app
st.title(f"Customise your Smoothie :cup_with_straw: ")
st.write(
  """Choose the fruits you want in your custom smoothie order!.
  """
)

# session = get_active_session()
cnx = st.connection("snowflake")      #updated
session = cnx.session()

name_on_order = st.text_input("Name of Smoothie")
st.write("The name of Smoothie will be: ", name_on_order)

# my_dataframe = session.table("smoothies.public.fruit_options")
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))

#convert snowpark dataframe to a Pandas Dataframe
pd_df=my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()


ingredients_list = st.multiselect (
    'Choose upto 5 ingredients:',
    my_dataframe,
    max_selections=5
    
)

if ingredients_list:   #if any ingredients exist
    
    ingredients_string = ''  #empty string
    
    for choosen_fruit in ingredients_list:
        ingredients_string += choosen_fruit + ' '

        #gives correct Search-on value
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
      
        st.subheader(choosen_fruit + 'Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        # smoothiefroot_response = requests.get("[https://my.smoothiefroot.com/api/fruit/watermelon](https://my.smoothiefroot.com/api/fruit/watermelon)")  
        
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    #sql
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string + """', '""" + name_on_order + """'
                    )"""
    #submit button
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, '+ name_on_order, icon="✅")


