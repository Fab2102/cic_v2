import streamlit as st
import pandas as pd
import time



st.set_page_config(page_title="Zinseszinsrechner", layout="centered", page_icon=":chart_with_upwards_trend:")
st.header("💶 Zinseszinsrechner")  

tab1, tab2 = st.tabs(["➗ Berechnung", "📈 Grafik"])
with tab1:
  
    st.subheader("Input")
    ### 1.row with 2 inputs
    row1_col1, row1_col2 = st.columns(2)
    starting_capital = row1_col1.number_input("Anfangskapital", min_value=0.00)
    annual_interest_rate = row1_col2.number_input("Zinsniveau p.a. (in %)", min_value=0.00)


    ### 2.row with 2 inputs
    row2_col1, row2_col2 = st.columns(2)
    time_period_years = row2_col1.number_input("Zeitraum (in Jahren)", min_value=0)
    compounding_frequency = row2_col2.selectbox("Verzinsungsart", ["jährlich", "quartalsweise", "monatlich"])


    ### 3.row with 2 inputs
    row3_col1, row3_col2 = st.columns(2)
    monthly_contribution = row3_col1.number_input("monatliche Rate", min_value=0.00)
    tax_rate = row3_col2.number_input("KESt (in %)", min_value=0.00)


    ### Toggling element for tax only once
    tax_once_at_the_end = st.toggle("KESt einmalig am Ende")


    class compound_interest_calculator:
        def __init__(self, starting_capital, annual_interest_rate, time_period_years, compounding_frequency, monthly_contribution, tax_rate):
            ### initiating variables
            self.starting_capital = starting_capital
            self.annual_interest_rate = (annual_interest_rate / 100)
            self.time_period_years = time_period_years
            self.compounding_frequency = compounding_frequency
            self.monthly_contribution = monthly_contribution
            self.tax_rate = (tax_rate / 100)
            
            ### initiating parameters for calculation
            self.k, self.multiplier_for_ebt, self.ebt_inpayments_graphic, self.interest_rate_per_period = self.calculate_parameters()
            
            ### Calculating results
            self.tgc = self.total_gross_capital()
            self.ebt, self.tax_to_pay, self.eat, self.inpayments = self.general_calculator()
            self.tnc = self.inpayments + self.eat
            self.df = self.dataframe_for_barchart()
            
            
            
        def calculate_parameters(self):
            if self.compounding_frequency == "jährlich":
                k = 1
                multiplier_for_ebt = 12
                ebt_inpayments_graphic = 0
            elif self.compounding_frequency == "quartalsweise":
                k = 4
                multiplier_for_ebt = 3
                ebt_inpayments_graphic = 0
            elif self.compounding_frequency == "monatlich":
                k = 12
                multiplier_for_ebt = 1
                ebt_inpayments_graphic = 0
                
            interest_rate_per_period = ((1 + self.annual_interest_rate) ** (1 / k)) - 1
            
            return k, multiplier_for_ebt, ebt_inpayments_graphic, interest_rate_per_period
            
            
            
        def total_gross_capital(self):
            if self.monthly_contribution == 0.00:
                tgc = (self.starting_capital * ((1 + self.annual_interest_rate) ** (1 / self.k)) ** (self.time_period_years * self.k))
            else:
                tgc = (self.starting_capital * ((1 + self.annual_interest_rate) ** (1 / self.k)) ** (self.time_period_years * self.k)) + (self.monthly_contribution * self.multiplier_for_ebt) * (((1 + self.annual_interest_rate) ** (1 / self.k)) ** (int(self.time_period_years) * self.k) - 1) / (((1 + self.annual_interest_rate) ** (1 / self.k)) - 1)
        
            return tgc
        
        
        
        def general_calculator(self):
            
            all_kest_per_period = []
            all_total_gross_capital_minus_tax = []
            current_capital = self.starting_capital
        
            if not tax_once_at_the_end:
                for i in range (1, self.time_period_years * self.k + 1):
                    kest_per_period = current_capital * self.interest_rate_per_period * self.tax_rate
                    all_kest_per_period.append(kest_per_period)
                    
                    total_gross_capital_minus_tax = (current_capital * (1 + self.interest_rate_per_period)) - (kest_per_period)
                    current_capital = total_gross_capital_minus_tax + self.monthly_contribution * self.multiplier_for_ebt
                    all_total_gross_capital_minus_tax.append(current_capital)
                    
                tax_to_pay = sum(all_kest_per_period)
                ebt = (self.tgc - (self.starting_capital + self.monthly_contribution * 12 * self.time_period_years)) if self.tgc else 0
                eat = (all_total_gross_capital_minus_tax[-1] - (self.starting_capital + self.monthly_contribution * 12 * self.time_period_years)) if all_total_gross_capital_minus_tax else 0
                total_inpayments = (self.starting_capital + self.monthly_contribution * 12 * self.time_period_years) if self.starting_capital else 0
            
            else:
                tax_to_pay = (self.tgc - (self.starting_capital + self.monthly_contribution * 12 * self.time_period_years)) * self.tax_rate
                ebt = self.tgc - (self.starting_capital + self.monthly_contribution * 12 * self.time_period_years)
                eat = ebt - tax_to_pay
                total_inpayments = (self.starting_capital + self.monthly_contribution * 12 * self.time_period_years) if self.starting_capital else 0
                
            return ebt, tax_to_pay, eat, total_inpayments
        
        
        def dataframe_for_barchart(self):
            list_of_inpayments = []
            list_of_interest = []
            years = list(range(1, 1 + self.time_period_years))
            
            for i in range(1, self.time_period_years + 1):
                payments = self.starting_capital + (self.monthly_contribution * 12 * i)
                list_of_inpayments.append(payments)
                
                if self.monthly_contribution == 0:
                    interest = (self.starting_capital * ((1 + self.annual_interest_rate) ** (1 / self.k)) ** (i * self.k)) - self.starting_capital - (self.monthly_contribution * 12 * i)
                    list_of_interest.append(interest)
                else:
                    interest = (self.starting_capital * ((1 + self.annual_interest_rate) ** (1 / self.k)) ** (i * self.k)) + (self.monthly_contribution * self.multiplier_for_ebt) * (((1 + self.annual_interest_rate) ** (1 / self.k)) ** (i * self.k) - 1) / (((1 + self.annual_interest_rate) ** (1 / self.k)) - 1) - self.starting_capital - (self.monthly_contribution * 12 * i)
                    list_of_interest.append(interest)
            
            df = pd.DataFrame({
        "Einzahlungen": list_of_inpayments,
        "Zinsen": list_of_interest,
        "Jahr": years})
        
            # Melten des DataFrames
            df_melted = pd.melt(df, id_vars="Jahr", value_vars=["Einzahlungen", "Zinsen"], var_name="Art", value_name="Betrag")

                
            return df_melted
        
    calc_metrics = compound_interest_calculator(starting_capital = starting_capital,
                                                annual_interest_rate = annual_interest_rate,
                                                time_period_years = time_period_years,
                                                compounding_frequency = compounding_frequency,
                                                monthly_contribution = monthly_contribution,
                                                tax_rate = tax_rate)
        
    
    
    ### display metrics
    
    #Bruttogesamtkapital
    #Nettogesamtkapital
    #Einzahlungen
    #Zinsgewinn vor Steuern
    #KESt
    #Zinsgewinn nach Steuern
    
    st.write("####")
    if calc_metrics.tgc and calc_metrics.ebt and calc_metrics.eat > 0:
        
        st.subheader("Ergebnisse")
    
        row1_yield = st.container()
        row2_yield = st.container()
        st.write("")
        row3_yield = st.container()
        st.write("")
        row4_yield = st.container()
        row5_yield = st.container()
        st.write("")
        row6_yield = st.container()

        with row1_yield:
            row1_col1, row1_col2 = st.columns([3,1])
            row1_col1.write("Gesamtkapital (Brutto)")
            row1_col2.write(f"{calc_metrics.tgc:,.0f} €")
        
        with row2_yield:
            row2_col1, row2_col2 = st.columns([3,1])
            row2_col1.write("Gesamtkapital (Netto)")
            row2_col2.write(f"{calc_metrics.tnc:,.0f} €")

        with row3_yield:
            row3_col1, row3_col2 = st.columns([3,1])
            row3_col1.write("Einzahlungen")
            row3_col2.write(f"{calc_metrics.inpayments:,.0f} €")

        with row4_yield:
            row4_col1, row4_col2 = st.columns([3,1])
            row4_col1.write("Zinsgewinn (Brutto)")
            row4_col2.write(f"{calc_metrics.ebt:,.0f} €")
        
        with row5_yield:
            row5_col1, row5_col2 = st.columns([3,1])
            row5_col1.write("Zinsgewinn (Netto)")
            row5_col2.write(f"{calc_metrics.eat:,.0f} €")
            
        with row6_yield:
            row6_col1, row6_col2 = st.columns([3,1])
            row6_col1.write("KESt")
            row6_col2.write(f"{calc_metrics.tax_to_pay:,.0f} €")
             

### display graphic
with tab2:
    
    with st.spinner("Mapping data..."):
        time.sleep(1.5)
        
        calc_metrics = compound_interest_calculator(starting_capital = starting_capital,
                                                annual_interest_rate = annual_interest_rate,
                                                time_period_years = time_period_years,
                                                compounding_frequency = compounding_frequency,
                                                monthly_contribution = monthly_contribution,
                                                tax_rate = tax_rate)
        
        chart_data = calc_metrics.df
        
    if calc_metrics.tgc > 0:
        st.vega_lite_chart(
    chart_data,
    {
        "mark": {"type": "bar", "tooltip": True},
        "encoding": {
            "x": {
                "field": "Jahr", 
                "type": "ordinal",  # Verwenden Sie ordinal für Balkenbreite
                "title": "Jahr",
                "axis": {
                    "labelAngle": 0  # Winkel der Beschriftung auf 0° setzen
                }
            },
            "y": {
                "field": "Betrag", 
                "type": "quantitative",
                "title": "Gesamtkapital (Brutto)",
            },
            "color": {
                "field": "Art", 
                "type": "nominal",
                "legend": {
                    "orient": "top"
                }
            },
            "tooltip": [
                {"field": "Jahr", "type": "ordinal"},
                {"field": "Betrag", "type": "quantitative", "format": ",.0f"},
                {"field": "Art", "type": "nominal"}
            ],
            "order": {
                "field": "Art",  # Sortiere nach dem Typ
                "sort": ["Einzahlung", "Zinsen"]  # Zinsen oben auf Einzahlungen
            }
        },
        "config": {
            "view": {
                "stroke": "transparent"  # Entfernt die Rahmenlinie um das Diagramm
            },
            "scale": {
                "band": {
                    "paddingInner": 0.2,  # Padding innerhalb der Balken
                    "paddingOuter": 0.2   # Padding außen um die Balken
                }
            }
        }
    },
    use_container_width=True
)
    else:
        st.warning("Werte eingeben um Grafik anzuzeigen.")