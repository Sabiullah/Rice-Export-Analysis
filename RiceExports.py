import mysql.connector
import pandas as pd
import numpy as np
import geopandas as gpd
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px

db_config = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "database": "riceexports"
}

# Establish the database connection
conn = mysql.connector.connect(**db_config)

# Create a cursor object
cursor = conn.cursor()

#with st.sidebar:
SELECT = option_menu(
    menu_title = None,
    options = ["About","Home","Export Analysis","Contact"],
    icons =["bar-chart","house","airplane","at"],
    default_index=2,
    orientation="horizontal",
    styles={"container": {"padding": "0!important", "background-color": "white","size":"auto", "width": "100%"},
        "icon": {"color": "black", "font-size": "15px"},
        "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px", "--hover-color": "#6F36AD"},
        "nav-link-selected": {"background-color": "#6F36AD"}})

#---------------------Basic Insights -----------------#
query = "SELECT * FROM ricedata"

# Execute the query and fetch data into a pandas DataFrame
ricedata = pd.read_sql(query, conn)



if SELECT == "Export Analysis":
    st.sidebar.write("Select a report:")
    report_choice = st.sidebar.radio(
        'Report',
        ["Importer/Exporter Overview", "Geographical Analysis", "Product Analysis", "Financial Analysis", "Time-Series Analysis"]
    )

    if report_choice == "Importer/Exporter Overview":
        # Creating tabs for Importer and Exporter
        tab_choice = st.sidebar.radio('Select', ["Importer", "Exporter"])

        if tab_choice == "Importer":
            ImporterCountry = ricedata['IMPORTER COUNTRY'].unique()
            sorted_countries = list(sorted(ImporterCountry))

            # Add a "Select All" option to the multiselect dropdown for Importer Countries
            Select_Import_Country = st.checkbox("Select All Importer Countries")

            if Select_Import_Country:
                selected_import_countries = ImporterCountry  # Select all countries if checkbox is checked
            else:
                selected_import_countries = st.multiselect("Select Importers:", sorted_countries)

            # Filter data based on selected countries
            filtered_import_data = ricedata[ricedata['IMPORTER COUNTRY'].isin(selected_import_countries)]
            # Aggregate quantity by country
            quantity_by_import_country = filtered_import_data.groupby('IMPORTER COUNTRY')[
                'QTY IN KG'].sum().reset_index()

            # Create a line chart using Plotly Express for Importers
            fig_import = px.line(quantity_by_import_country, x='IMPORTER COUNTRY', y='QTY IN KG',
                                 labels={'IMPORTER COUNTRY': 'Country', 'QTY IN KG': 'Quantity'})
            st.plotly_chart(fig_import)

            # Check if Importer Country selection is not empty
            if selected_import_countries is not None and np.any(selected_import_countries):
                # Filter Importer Names based on selected countries
                importer_names = filtered_import_data['IMPORTER NAME'].unique()
                sorted_importer_names = list(sorted(importer_names))

                # Add a "Select All" option to the multiselect dropdown for Importer Names
                Select_Import_Name = st.checkbox("Select All Importer Names")

                if Select_Import_Name:
                    selected_importer_names = importer_names  # Select all names if checkbox is checked
                else:
                    selected_importer_names = st.multiselect("Select Importer Names:", sorted_importer_names)

                # Filter data based on selected importer names
                filtered_importer_names_data = filtered_import_data[
                    filtered_import_data['IMPORTER NAME'].isin(selected_importer_names)
                ]
                # Aggregate quantity by importer name
                quantity_by_importer_name = filtered_importer_names_data.groupby('IMPORTER NAME')[
                    'QTY IN KG'].sum().reset_index()

                # Create a line chart using Plotly Express for Importer Names
                fig_importer_name = px.line(quantity_by_importer_name, x='IMPORTER NAME', y='QTY IN KG',
                                            labels={'IMPORTER NAME': 'Importer Name', 'QTY IN KG': 'Quantity'})
                st.plotly_chart(fig_importer_name)




        elif tab_choice == "Exporter":
            ExporterCountry = ricedata['EXPORTER NAME'].unique()

            # Add a "Select All" option to the multiselect dropdown
            Select_Export_Country = st.checkbox("Select All Exporter Names")

            if Select_Export_Country:
                selected_export_countries = ExporterCountry  # Select all countries if checkbox is checked
            else:
                selected_export_countries = st.multiselect("Select Exporters:", ExporterCountry)

            # Filter data based on selected countries
            filtered_export_data = ricedata[ricedata['EXPORTER NAME'].isin(selected_export_countries)]
            # Aggregate quantity by country for the entire dataset
            quantity_by_country_all = ricedata.groupby('EXPORTER NAME')['QTY IN KG'].sum().reset_index()
            # Aggregate quantity by country
            quantity_by_export_country = filtered_export_data.groupby('EXPORTER NAME')['QTY IN KG'].sum().reset_index()

            # Create a line chart using Plotly Express for Exporters
            fig_export = px.line(quantity_by_export_country, x='EXPORTER NAME', y='QTY IN KG',
                                 labels={'EXPORTER NAME': 'Country', 'QTY IN KG': 'Quantity'})
            st.plotly_chart(fig_export)

            # Allow selection of top N exporters based on quantity
            top_n_exporters = st.number_input("Select top N exporters", min_value=1, max_value=len(quantity_by_country_all),
                                              value=3)

            # Get top N exporters by quantity
            top_exporters = quantity_by_country_all.nlargest(top_n_exporters, 'QTY IN KG')

            # Create a line chart using Plotly Express for top exporters
            fig_top_exporters = px.line(top_exporters, x='EXPORTER NAME', y='QTY IN KG',
                                        labels={'EXPORTER NAME': 'Country', 'QTY IN KG': 'Quantity'})
            st.plotly_chart(fig_top_exporters)


#******************************************************************************************************
#******************************************************************************************************

    if report_choice == "Geographical Analysis":
        st.write("### Geographical Analysis")

        # Add filtering options
        filter_options = st.radio("Filter by:", ("All Countries", "Select Multiple Countries", "Top N Countries"))

        if filter_options == "All Countries":
            quantity_by_importer_country = ricedata.groupby('IMPORTER COUNTRY')['QTY IN KG'].sum().reset_index()
        elif filter_options == "Select Multiple Countries":
            selected_countries = st.multiselect("Select Countries:", ricedata['IMPORTER COUNTRY'].unique())
            quantity_by_importer_country = \
            ricedata[ricedata['IMPORTER COUNTRY'].isin(selected_countries)].groupby('IMPORTER COUNTRY')[
                'QTY IN KG'].sum().reset_index()
        else:  # Top N Countries
            top_n = st.number_input("Select top N countries", min_value=1,
                                    max_value=len(ricedata['IMPORTER COUNTRY'].unique()), value=5)
            quantity_by_importer_country = ricedata.groupby('IMPORTER COUNTRY')['QTY IN KG'].sum().nlargest(
                top_n).reset_index()

        # Create a choropleth map using Plotly Express
        fig = px.choropleth(quantity_by_importer_country,
                            locations='IMPORTER COUNTRY',
                            locationmode="country names",
                            color='QTY IN KG',
                            hover_name='IMPORTER COUNTRY',
                            color_continuous_scale='YlGnBu',
                            labels={'IMPORTER COUNTRY': 'Country', 'QTY IN KG': 'Quantity'})

        # Display the map using Streamlit
        st.plotly_chart(fig)

#*********************************************************************************************
#*********************************************************************************************

    if report_choice == "Product Analysis":
        st.write("### Product Analysis")

        analysis_option = st.radio("Select Analysis Option:", ("Country-wise", "Product-wise"))

        if analysis_option == "Country-wise":
            filter_options = st.radio("Filter by:", ("All Import Countries", "Top N Import Countries"))

            if filter_options == "All Import Countries":
                # Group by 'IMPORTER COUNTRY' and 'HS CODE DESCRIPTION' and sum the quantities
                product_analysis = ricedata.groupby(['IMPORTER COUNTRY', 'HS CODE DESCRIPTION'])[
                    'QTY IN KG'].sum().reset_index()
                st.write(
                    "### Import Details for All Import Countries based on HS CODE DESCRIPTION and Quantity (in KG)")
                st.write(product_analysis)
            else:  # Top N Import Countries
                top_n = st.number_input("Select top N import countries", min_value=1,
                                        max_value=len(ricedata['IMPORTER COUNTRY'].unique()), value=5)
                top_countries = ricedata.groupby('IMPORTER COUNTRY')['QTY IN KG'].sum().nlargest(top_n).index.tolist()

                # Filter data based on the top N import countries
                filtered_data = ricedata[ricedata['IMPORTER COUNTRY'].isin(top_countries)]

                # Group by 'IMPORTER COUNTRY' and 'HS CODE DESCRIPTION' and sum the quantities
                product_analysis = filtered_data.groupby(['IMPORTER COUNTRY', 'HS CODE DESCRIPTION'])[
                    'QTY IN KG'].sum().reset_index()
                st.write(
                    f"### Import Details for Top {top_n} Import Countries based on HS CODE DESCRIPTION and Quantity (in KG)")
                st.write(product_analysis)
        else:  # Product-wise analysis
            product_option = st.radio("Select Product Option:", ("All Products", "Top N Products"))

            if product_option == "All Products":
                # Group by 'HS CODE DESCRIPTION' and sum the quantities
                product_analysis = ricedata.groupby('HS CODE DESCRIPTION')['QTY IN KG'].sum().reset_index()
                st.write("### Import Details for All Products based on HS CODE DESCRIPTION and Quantity (in KG)")
                st.write(product_analysis)
            else:  # Top N Products
                top_n_products = st.number_input("Select top N products", min_value=1,
                                                 max_value=len(ricedata['HS CODE DESCRIPTION'].unique()), value=5)

                # Group by 'HS CODE DESCRIPTION' and sum the quantities
                product_analysis = ricedata.groupby('HS CODE DESCRIPTION')['QTY IN KG'].sum().nlargest(
                    top_n_products).reset_index()
                st.write(
                    f"### Import Details for Top {top_n_products} Products based on HS CODE DESCRIPTION and Quantity (in KG)")
                st.write(product_analysis)
#***********************************************************************************************************************
#***********************************************************************************************************************

    if report_choice == "Financial Analysis":
        st.write("### Financial Analysis")

        analysis_option = st.radio("Select Analysis Option:", ("Country-wise", "Currency-wise"))

        if analysis_option == "Country-wise":
            filter_options = st.radio("Filter by:", ("All Import Countries", "Top N Import Countries"))

            if filter_options == "All Import Countries":
                # Group by 'IMPORTER COUNTRY' and 'CURRENCY' and sum the import values
                financial_analysis = ricedata.groupby(['IMPORTER COUNTRY', 'CURRENCY'])[
                    ['IMPORT VALUE FOB', 'QTY IN KG']].sum().reset_index()
                financial_analysis['AVG RATE PER KG'] = financial_analysis['IMPORT VALUE FOB'] / financial_analysis[
                    'QTY IN KG']
                st.write("### Financial Details for All Import Countries based on Currency and Import Value FOB")
                st.write(financial_analysis)
            else:  # Top N Import Countries
                top_n = st.number_input("Select top N import countries", min_value=1,
                                        max_value=len(ricedata['IMPORTER COUNTRY'].unique()), value=5)
                top_countries = ricedata.groupby('IMPORTER COUNTRY')['IMPORT VALUE FOB'].sum().nlargest(
                    top_n).index.tolist()

                # Filter data based on the top N import countries
                filtered_data = ricedata[ricedata['IMPORTER COUNTRY'].isin(top_countries)]

                # Group by 'IMPORTER COUNTRY' and 'CURRENCY' and sum the import values
                financial_analysis = filtered_data.groupby(['IMPORTER COUNTRY', 'CURRENCY'])[
                    ['IMPORT VALUE FOB', 'QTY IN KG']].sum().reset_index()
                financial_analysis['AVG RATE PER KG'] = financial_analysis['IMPORT VALUE FOB'] / financial_analysis[
                    'QTY IN KG']
                st.write(
                    f"### Financial Details for Top {top_n} Import Countries based on Currency and Import Value in FOB")
                st.write(financial_analysis)
        else:  # Currency-wise analysis
            currency_option = st.radio("Select Currency Option:",
                                       ("All Currencies", "Top N Currencies", "Currency-wise Summary"))

            if currency_option == "All Currencies":
                # Group by 'CURRENCY' and sum the import values
                financial_analysis = ricedata.groupby('CURRENCY')[['IMPORT VALUE FOB', 'QTY IN KG']].sum().reset_index()
                financial_analysis['AVG RATE PER KG'] = financial_analysis['IMPORT VALUE FOB'] / financial_analysis[
                    'QTY IN KG']
                st.write("### Financial Details for All Currencies based on Currency and Import Value in FOB")
                st.write(financial_analysis)
            elif currency_option == "Top N Currencies":
                top_n_currencies = st.number_input("Select top N currencies", min_value=1,
                                                   max_value=len(ricedata['CURRENCY'].unique()), value=5)
                currency_import_totals = ricedata.groupby('CURRENCY')['IMPORT VALUE FOB'].sum().reset_index()

                # Select top N currencies based on total import value
                top_currencies = currency_import_totals.nlargest(top_n_currencies, 'IMPORT VALUE FOB')['CURRENCY']

                # Group by 'CURRENCY' and sum the import values
                financial_analysis = ricedata[ricedata['CURRENCY'].isin(top_currencies)]
                financial_analysis = financial_analysis.groupby('CURRENCY')[
                    ['IMPORT VALUE FOB', 'QTY IN KG']].sum().reset_index()
                financial_analysis['AVG RATE PER KG'] = financial_analysis['IMPORT VALUE FOB'] / financial_analysis[
                    'QTY IN KG']
                st.write(
                    f"### Financial Details for Top {top_n_currencies} Currencies based on Currency and Import Value FOB")
                st.write(financial_analysis)
            else:  # Currency-wise Summary
                # Group by 'CURRENCY' and sum the import values for the summary
                currency_summary = ricedata.groupby('CURRENCY')[['IMPORT VALUE FOB', 'QTY IN KG']].sum().reset_index()
                currency_summary['AVG RATE PER KG'] = currency_summary['IMPORT VALUE FOB'] / currency_summary[
                    'QTY IN KG']
                summary_sorted = currency_summary.sort_values(by = 'IMPORT VALUE FOB', ascending=False)
                st.write("### Currency-wise Summary based on Currency and Import Value FOB")
                st.write(summary_sorted)

#**********************************************************************************************************
#**********************************************************************************************************

    if report_choice == "Time-Series Analysis":
        st.write("### Time-Series Analysis")

        analysis_option = st.radio("Select Analysis Option:", (
        "Country-wise", "Year-wise", "Top N Transactions by Year and Country"))

        if analysis_option == "Country-wise":
            # Filter by country
            country_option = st.multiselect("Select Country/Countries:", ricedata['IMPORTER COUNTRY'].unique())

            if not country_option:  # If no country selected
                st.warning("Please select at least one country.")
            else:
                filtered_data = ricedata[ricedata['IMPORTER COUNTRY'].isin(country_option)]
                # Group by country and year, sum the quantities
                country_year_analysis = \
                    filtered_data.groupby(['IMPORTER COUNTRY', filtered_data['ARRIVAL DATE'].dt.year])[
                        'QTY IN KG'].sum().reset_index()
                st.write("### Quantity (in KG) Time-Series Analysis for Selected Country/Countries")
                st.write(country_year_analysis)

                # Line chart for selected country/countries
                fig_country = px.line(country_year_analysis, x='IMPORTER COUNTRY', y='QTY IN KG', color='ARRIVAL DATE')
                fig_country.update_layout(xaxis_title='Country', yaxis_title='Quantity (in KG)',
                                          title='Country-wise Yearly Analysis')
                st.plotly_chart(fig_country)


        elif analysis_option == "Year-wise":
            # Get unique countries
            all_countries = ricedata['IMPORTER COUNTRY'].unique()
            country_option = st.multiselect("Select Country/Countries:", ['All Countries'] + all_countries.tolist(),
                                            default=['All Countries'])

            # Filter data based on country selection
            if 'All Countries' in country_option:
                filtered_data = ricedata.copy()  # Keep original data for all countries
            else:
                filtered_data = ricedata[ricedata['IMPORTER COUNTRY'].isin(country_option)]

            # Group by year and sum the quantities
            year_analysis = filtered_data.groupby(filtered_data['ARRIVAL DATE'].dt.year)[
                'QTY IN KG'].sum().reset_index()
            st.write("### Quantity (in KG) Time-Series Analysis for All Years")

            # Line chart for selected countries or all countries
            fig_year = px.line(year_analysis, x='ARRIVAL DATE', y='QTY IN KG', title='Year-wise Analysis')
            if len(country_option) > 1:  # For multiple selected countries, modify title and legend
                fig_year.update_traces(name='Selected Countries')
                fig_year.update_layout(title='Year-wise Analysis for Selected Countries', xaxis_title='Year',
                                       yaxis_title='Quantity (in KG)')
            else:
                fig_year.update_layout(xaxis_title='Year', yaxis_title='Quantity (in KG)')
            st.plotly_chart(fig_year)


        elif analysis_option == "Top N Transactions by Year and Country":
            all_years = ricedata['ARRIVAL DATE'].dt.year.unique()
            selected_year = st.selectbox("Select Year:", all_years)
            filtered_by_year = ricedata[ricedata['ARRIVAL DATE'].dt.year == selected_year]
            top_n = st.number_input("Select top N transactions", min_value=1, value=5)

            # Group by year, country, and transaction ID, sum the quantities
            transactions_by_year_country = round(filtered_by_year.groupby([
                'IMPORTER COUNTRY'
            ])['QTY IN KG'].sum().reset_index(),0)

            # Group by year and country, count the number of transactions
            transaction_count_by_year_country = filtered_by_year.groupby(
                ['IMPORTER COUNTRY']).size().reset_index(name='Transaction Count')

            # Calculate average quantity per transaction and round to zero decimal places
            transaction_count_by_year_country['Avg Qty per Transaction'] = round(
                transactions_by_year_country['QTY IN KG'] / transaction_count_by_year_country['Transaction Count'], 0)

            # Sort transaction count table by Transaction Count in descending order
            transaction_count_by_year_country = transaction_count_by_year_country.sort_values('Transaction Count',
                                                                                              ascending=False)

            # Sort by quantity and select top N transactions
            top_transactions = transactions_by_year_country.sort_values('QTY IN KG', ascending=False).head(top_n)

            # Filter the line chart data to show only the top N countries based on transactions
            top_countries = top_transactions['IMPORTER COUNTRY'].tolist()

            filtered_transactions_by_country = transactions_by_year_country[
                transactions_by_year_country['IMPORTER COUNTRY'].isin(top_countries)]

            st.write(f"### Top {top_n} Transactions for {selected_year} by Country based on Quantity")
            st.write(top_transactions)
            st.write(f"### Transaction Count for {selected_year} by Country")
            st.write(transaction_count_by_year_country)

            # Line chart for transaction count by year and country
            fig_top_transactions = px.line(filtered_transactions_by_country, x='IMPORTER COUNTRY', y='QTY IN KG',
                                           labels={'QTY IN KG': 'Quantity (in KG)', 'IMPORTER COUNTRY': 'Country'},
                                           title=f'Top {top_n} Transactions for {selected_year} by Country based on Quantity')

            fig_top_transactions.update_layout(xaxis_title='Country', yaxis_title='Quantity (in KG)')
            st.plotly_chart(fig_top_transactions)

            fig_transaction_count = px.line(transaction_count_by_year_country, x='IMPORTER COUNTRY',
                                            y='Transaction Count',
                                            labels={'Transaction Count': 'Transaction Count',
                                                    'IMPORTER COUNTRY': 'Country'},
                                            title=f'Transaction Count for {selected_year} by Country')

            fig_transaction_count.update_layout(xaxis_title='Country', yaxis_title='Transaction Count')
            st.plotly_chart(fig_transaction_count)
