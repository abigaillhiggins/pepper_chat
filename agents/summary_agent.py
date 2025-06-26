import re
from langchain_openai import ChatOpenAI
import requests
from datetime import datetime
import pytz

class SummaryAgent:
    def __init__(self):
        # LLM for processing and filtering responses
        self.llm = ChatOpenAI(temperature=0.2, model_name="gpt-4o")
        
        # Australian context
        self.location = "UC Collaborative Robotics Lab, Canberra, Australia"
        self.timezone = pytz.timezone('Australia/Canberra')
        
        # Australian public holidays (major ones)
        self.australian_holidays = {
            "new year's day": "January 1",
            "australia day": "January 26", 
            "good friday": "varies",
            "easter monday": "varies",
            "anzac day": "April 25",
            "queen's birthday": "second Monday in June",
            "christmas day": "December 25",
            "boxing day": "December 26",
            "labour day": "varies by state",
            "easter sunday": "varies",
            "easter saturday": "varies"
        }

    def convert_to_metric(self, text):
        """Convert imperial units to metric units in text."""
        # Temperature conversions (Fahrenheit to Celsius)
        fahrenheit_pattern = r'(\d+(?:\.\d+)?)\s*°?F|(\d+(?:\.\d+)?)\s*degrees?\s*fahrenheit'
        def f_to_c(match):
            f_temp = float(match.group(1) or match.group(2))
            c_temp = (f_temp - 32) * 5/9
            return f"{c_temp:.1f}°C"
        text = re.sub(fahrenheit_pattern, f_to_c, text, flags=re.IGNORECASE)
        
        # Distance conversions (miles to kilometers)
        miles_pattern = r'(\d+(?:\.\d+)?)\s*miles?'
        def miles_to_km(match):
            miles = float(match.group(1))
            km = miles * 1.60934
            return f"{km:.1f} kilometres"
        text = re.sub(miles_pattern, miles_to_km, text, flags=re.IGNORECASE)
        
        # Weight conversions (pounds to kilograms)
        pounds_pattern = r'(\d+(?:\.\d+)?)\s*pounds?|(\d+(?:\.\d+)?)\s*lbs?'
        def lbs_to_kg(match):
            lbs = float(match.group(1) or match.group(2))
            kg = lbs * 0.453592
            return f"{kg:.1f} kilograms"
        text = re.sub(pounds_pattern, lbs_to_kg, text, flags=re.IGNORECASE)
        
        # Height conversions (feet/inches to centimeters)
        feet_inches_pattern = r'(\d+)\s*feet?\s*(\d+)\s*inches?'
        def feet_inches_to_cm(match):
            feet = int(match.group(1))
            inches = int(match.group(2))
            total_inches = feet * 12 + inches
            cm = total_inches * 2.54
            return f"{cm:.1f} centimetres"
        text = re.sub(feet_inches_pattern, feet_inches_to_cm, text, flags=re.IGNORECASE)
        
        return text

    def filter_australian_holidays(self, text, query):
        """Filter holiday information to be relevant to Australia."""
        query_lower = query.lower()
        if any(holiday_word in query_lower for holiday_word in ["holiday", "public holiday", "bank holiday"]):
            # Check if the response mentions non-Australian holidays
            non_australian_holidays = [
                "thanksgiving", "independence day", "memorial day", "labor day", 
                "columbus day", "veterans day", "presidents day", "martin luther king day",
                "groundhog day", "super bowl", "black friday", "cyber monday"
            ]
            
            for holiday in non_australian_holidays:
                if holiday in text.lower():
                    # Replace with Australian context
                    current_date = datetime.now(self.timezone)
                    if "thanksgiving" in text.lower():
                        return f"Thanksgiving is not celebrated in Australia. Today is {current_date.strftime('%A, %B %d')} in Canberra."
                    elif "independence day" in text.lower():
                        return f"Independence Day is not an Australian holiday. Australia Day is celebrated on January 26th."
                    else:
                        return f"That holiday is not celebrated in Australia. Today is {current_date.strftime('%A, %B %d')} in Canberra."
        
        return text

    def add_australian_context(self, text, query):
        """Add Australian context to responses when relevant."""
        query_lower = query.lower()
        
        # Add location context for weather/time queries
        if "weather" in query_lower:
            if "canberra" not in text.lower() and "australia" not in text.lower():
                text = f"In Canberra, Australia: {text}"
        
        # Add timezone context for time queries
        if "time" in query_lower:
            if "canberra" not in text.lower() and "australia" not in text.lower():
                current_time = datetime.now(self.timezone)
                text = f"In Canberra, Australia: {text} (Current time: {current_time.strftime('%I:%M %p')})"
        
        return text

    def rewrite_symbols_phonetically(self, text):
        """Rewrite symbols like °C, km, kg, cm, % phonetically for TTS."""
        # Replace °C with degrees Celsius
        text = re.sub(r"°C", " degrees Celsius", text)
        # Replace km with kilometres (if not already part of a word)
        text = re.sub(r"\bkm\b", "kilometres", text)
        # Replace kg with kilograms
        text = re.sub(r"\bkg\b", "kilograms", text)
        # Replace cm with centimetres
        text = re.sub(r"\bcm\b", "centimetres", text)
        # Replace % with percent
        text = re.sub(r"%", " percent", text)
        return text

    def summarize_and_filter(self, search_response, original_query):
        """Summarize and filter the search response for Australian context."""
        try:
            # First, apply basic conversions
            filtered_text = self.convert_to_metric(search_response)
            
            # Filter for Australian holidays
            filtered_text = self.filter_australian_holidays(filtered_text, original_query)
            
            # Add Australian context
            filtered_text = self.add_australian_context(filtered_text, original_query)
            
            # Use LLM to create a concise, Australian-focused summary
            system_prompt = """You are a helpful assistant at the UC Collaborative Robotics Lab in Canberra, Australia. 
            Summarize information to be relevant to Australians, using metric units and Australian context.
            Keep responses under 200 characters, natural and engaging.
            Focus on information that would be useful to someone in Canberra, Australia."""
            
            user_prompt = f"Original query: {original_query}\nSearch response: {filtered_text}\n\nCreate an Australian-focused summary:"
            
            response = self.llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]).content.strip()
            
            # Rewrite symbols phonetically for TTS
            response = self.rewrite_symbols_phonetically(response)
            return response
            
        except Exception as e:
            print(f"Error in SummaryAgent.summarize_and_filter: {str(e)}")
            # Fallback: return the filtered text without LLM processing
            return self.rewrite_symbols_phonetically(filtered_text)

    def get_response(self, search_response, original_query):
        """Get a filtered and summarized response."""
        return self.summarize_and_filter(search_response, original_query) 