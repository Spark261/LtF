from otree.api import *
import matplotlib.pyplot as plt
import io
import base64
import math 

doc = """
Simple trust game
"""


class C(BaseConstants):
    NAME_IN_URL = 'cobweb'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3    
    CONSTANT = 60
    COEF = 0.95    
    
#FUNCTIONS


class Subsession(BaseSubsession):
    is_shown = models.BooleanField(initial=False) 

class Player(BasePlayer):
    exp = models.FloatField(min=0, max=900,
                            doc="""expectation for t=t""",
                            label="what is your prediction of the market price?",
                            )
    
    payoffs = models.FloatField()
    
    
class Group(BaseGroup):
    market_price = models.FloatField()
    RN = models.PositiveIntegerField()


# PAGES
# PAGES for round 1
class PageOne(Page):
    form_model = 'player'
    form_fields = ['exp']
    
    def is_displayed(player: Player):
        return player.round_number == 1
    

class WaitPageeOne(WaitPage):         
    
    def after_all_players_arrive(group):
        others = [p.exp for p in group.get_players()]
        avg = sum(others) / len(others) if others else 0
        market_price = C.CONSTANT + C.COEF * avg
        group.market_price = market_price
        
        for player in group.get_players():
            player.payoffs = int(math.ceil(abs(group.market_price - player.exp)))
    
    def is_displayed(player: Player):
        return player.round_number == 1
    
class ResultsOne(Page):
    def is_displayed(player: Player):
        return player.round_number == 1
      

#----------------------------
# PAGES for round 2 and subsequent rounds    
class Choice(Page):
    form_model = 'player'
    form_fields = ['exp']
    
    def vars_for_template(self):
        previous_round = self.in_round(self.round_number - 1)
        previous_exp = previous_round.exp if previous_round else None
        previous_market_price = previous_round.group.market_price if previous_round else None
        previous_payoffs = int(previous_round.payoffs if previous_round else None)
       
        # Create a line graph for exp and market_price history
        fig, ax = plt.subplots()
        rounds = [r.round_number for r in self.in_previous_rounds()]
        exp_history = [p.exp for p in self.in_previous_rounds()]  # Include the current round's exp
        market_price_history = [p.group.market_price for p in self.in_previous_rounds()]
        
        # Change the color of the "Your prediction" line and dots to black
        ax.plot(rounds, market_price_history, marker='o', markersize=4, linewidth=1, label='Actual price')
        ax.plot(rounds, exp_history, marker='o', markersize=4, linewidth=1, color='black', label='Your prediction')
        
        # Set legend to the center-right of the graph
        ax.legend(loc='center left', bbox_to_anchor=(1.05, 0.5), borderaxespad=0.)
        
        ax.set_xticks(rounds)  # Set X-axis ticks to match the round numbers
        ax.set_title('Your prediction vs. actual market prices', loc='center', pad=20)
        ax.set_xlabel('Round')
        ax.set_ylabel('Price')
        ax.grid(which='major', axis='y', linestyle='-', linewidth='0.2', color='gray')  # Make horizontal grid lines more subtle

        # Convert the plot to an image and embed it in the HTML
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        graph = base64.b64encode(buffer.getvalue()).decode()
        
        
        
        return {
            'previous_exp': previous_exp,
            'previous_market_price': previous_market_price,
            'previous_payoffs': previous_payoffs,
            'graph': graph,
        }      
        

    def is_displayed(self):
        return 1 < self.round_number < C.NUM_ROUNDS
    
    
    
class WaitPagee(WaitPage):             
    def after_all_players_arrive(group):
        others = [p.exp for p in group.get_players()]
        avg = sum(others) / len(others) if others else 0
        market_price = C.CONSTANT + C.COEF * avg
        group.market_price = market_price
        
        for player in group.get_players():
            player.payoffs = int(math.ceil(abs(group.market_price - player.exp)))
    
    def is_displayed(self):
        return 1 < self.round_number < C.NUM_ROUNDS    
    
    
class Results(Page):
    def vars_for_template(self):
        previous_round = self.in_round(self.round_number - 1)
        previous_exp = previous_round.exp if previous_round else None
        previous_market_price = previous_round.group.market_price if previous_round else None
        previous_payoffs = int(previous_round.payoffs if previous_round else None)
       
        # Create a line graph for exp and market_price history
        fig, ax = plt.subplots()
        rounds = [r.round_number for r in self.in_previous_rounds()]
        exp_history = [p.exp for p in self.in_previous_rounds()]  # Include the current round's exp
        market_price_history = [p.group.market_price for p in self.in_previous_rounds()]
        
        # Change the color of the "Your prediction" line and dots to black
        ax.plot(rounds, market_price_history, marker='o', markersize=4, linewidth=1, label='Actual price')
        ax.plot(rounds, exp_history, marker='o', markersize=4, linewidth=1, color='black', label='Your prediction')
        
        # Set legend to the center-right of the graph
        ax.legend(loc='center left', bbox_to_anchor=(1.05, 0.5), borderaxespad=0.)
        
        ax.set_xticks(rounds)  # Set X-axis ticks to match the round numbers
        ax.set_title('Your prediction vs. actual market prices', loc='center', pad=20)
        ax.set_xlabel('Round')
        ax.set_ylabel('Price')
        ax.grid(which='major', axis='y', linestyle='-', linewidth='0.2', color='gray')  # Make horizontal grid lines more subtle

        # Convert the plot to an image and embed it in the HTML
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        graph = base64.b64encode(buffer.getvalue()).decode()
        
        
        return {
            'previous_exp': previous_exp,
            'previous_market_price': previous_market_price,
            'previous_payoffs': previous_payoffs,
            'graph': graph,
        } 
        

    
    def is_displayed(self):
        return self.round_number == C.NUM_ROUNDS
    
    
class FinalPage(Page):  
    def vars_for_template(self):
        total_payoffs = sum(n.payoffs for n in self.in_previous_rounds())
        
        return {
            'total_payoffs': total_payoffs,
        }
    
    def is_displayed(self):
        return self.round_number == C.NUM_ROUNDS    
    
   
 


        
page_sequence = [PageOne, WaitPageeOne, ResultsOne, Choice, WaitPagee, Results, FinalPage]


