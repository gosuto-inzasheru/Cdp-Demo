"""
  Sim of CDP System

  ### SYSTEM STATE ###

  Global Collateral Ratio
  Total Deposits
  Total Debt

  ### SYSTEM CONFIG ###

  Max LTV
  Fee per second (0% on LUSD)
  Origination Fee (Fixed Fee 50 BPS on LUSD)

  ### TROVE STATE ###

  Local Collateral Ratio
  Local Deposits
  Local Debt


  ### USER ACTIONS ###
  Deposit
  Withdraw

  Borrow
  Repay

  Liquidate
"""
import math
import random
from rich.pretty import pprint

from lib.names import name_list


MAX_BPS = 10_000
SECONDS_SINCE_DEPLOY = 0
SECONDS_PER_TURN = 12 ## One block in POS
INITIAL_FEED = 1000
SPEED_RANGE = 10


class Ebtc:
    def __init__(self):
        self.MAX_LTV = 15000  ## 150%
        self.FEE_PER_SECOND = 0  ## No fee for borrows
        self.ORIGINATION_FEE = 50  ## 50BPS

        self.total_deposits = 0
        self.total_debt = 0
        self.feed = INITIAL_FEED
        self.time = SECONDS_SINCE_DEPLOY
        self.turn = 0

    def __repr__(self):
        return str(self.__dict__)

    def collateral_ratio(self):
        return self.total_debt * MAX_BPS / self.total_deposits

    def max_borrow(self):
        return self.total_debt * self.feed

    def is_in_emergency_mode(self):
        ## TODO:
        return False

    def is_solvent(self):
        ## NOTE: Strictly less to avoid rounding, etc..
        return self.total_debt < self.max_borrow()

    def set_feed(self, value):
      self.feed = value

    
    def take_turn(self, users, troves):
        print("Turn", self.turn, ": Second: ", self.time)

        ## Do w/e
        self.sort_users(users)

        self.take_actions(users, troves)

        ## TODO: Logging here for charting
        
        ## Increase counter
        self.next_turn()
        
    
    def sort_users(self, users):
        def get_key(user):
            ## TODO: Swing size (+- to impact randomness, simulate sorting, front-running etc..)
            return user.speed * random.random()
        users.sort(key=get_key)
    
    def take_actions(self, users, troves):
        ## TODO: Add User Decisions making / given the list of all trove have user do something
        for user in users:
            user.take_action(self.turn, troves)

    def next_turn(self):
      self.time += SECONDS_PER_TURN
      self.turn += 1
  
    


class Trove:
    def __init__(self, owner, system):
        self.deposits = 0
        self.debt = 0
        self.last_update_ts = system.time
        self.owner = owner
        self.system = system

    def __repr__(self):
        return str(self.__dict__)

    def local_collateral_ratio(self):
        return self.debt * MAX_BPS / self.deposits

    def deposit(self, amount):
        self.system.total_deposits += amount
        self.deposits += amount
        self.owner.reduce_balance(self, amount)

    def withdraw(self, amount):
        self.deposits -= amount
        assert self.is_solvent()

    def borrow(self, amount):
        self.debt += amount
        assert self.is_solvent()
        self.system.total_debt += amount
        assert self.system.is_solvent()

    def repay(self, amount):
        ## TODO
        return 0

    def liquidate(self, amount, caller):
        ## Only if not owner
        if caller == self.owner:
            return False

        return 0

    ## SECURITY CHECKS
    def is_trove(self):
        return True

    def max_borrow(self):
        return self.deposits * self.system.feed

    def is_solvent(self):
        ## Strictly less to avoid rounding or w/e
        return self.debt < self.max_borrow()


class User:
    def __init__(self, initial_balance_collateral):
        self.collateral = initial_balance_collateral
        self.name = random.choice(name_list)
        self.speed = math.floor(random.random() * SPEED_RANGE) + 1

    def __repr__(self):
        return str(self.__dict__)

    def increase_balance(self, caller, amount):
        try:
            assert caller.is_trove() == True
            self.collateral += amount
        except:
            ## Do nothing on failure
            print("error")

    def reduce_balance(self, caller, amount):
        try:
            assert caller.is_trove() == True
            self.collateral -= amount
        except:
            ## Do nothing on failure
            print("error")

    def get_balance(self):
        return self.collateral

    def take_action(self, turn, troves):
        print("User" , self.name, " Taking Action")
        print("turn ", turn)


## POOL For Swap

class UniV2Pool():
  def __init__(self, start_x, start_y, start_lp):
    ## NOTE: May or may not want to have a function to hardcode this
    self.reserve_x = start_x
    self.reserve_y = start_y
    self.total_supply = start_lp

  def k(self):
    return self.x * self.y
  
  def get_price_out(self, is_x, amount):
    if (is_x):
      return self.get_price(amount, self.reserve_x, self.reserve_y)
    else:
      return self.get_price(amount, self.reserve_y, self.reserve_x)

  ## UniV2 Formula, can extend the class and change this to create new pools
  def get_price(amount_in, reserve_in, reserve_out):
      amountInWithFee = amount_in * 997
      numerator = amountInWithFee * reserve_out
      denominator = reserve_in * 1000 + amountInWithFee
      amountOut = numerator / denominator

      return amountOut
  
  def withdraw_lp():
    ## TODO
    return False
  
  def lp():
    ## TODO
    return False
  

## TODO: Add Roles ##

## Borrows and Holds
class Borrower(User):
    def step():
        pass


## Borrow and Sells when price is higher
class LongArbitrager(User):
    def step():
        pass


## Buys when cheap and sells when higher
class ShortArbitrager(User):
    def step():
        pass


## Does both arbitrages
class Trader(User):
    def step():
        pass


def main():
    # init the system
    system = Ebtc()

    # init a user with a balance of 100
    user_1 = Borrower(100)

    # init a trove for this user
    trove_1 = Trove(user_1, system)
    pprint(trove_1.__dict__)

    # make a deposit into the system
    trove_1.deposit(25)
    pprint(trove_1.__dict__)

    # borrow against this deposit
    trove_1.borrow(12.5)
    pprint(trove_1.__dict__)

    assert system.time == 0

    ## Test for Feed and solvency
    assert trove_1.is_solvent()

    system.set_feed(0)

    assert not trove_1.is_solvent()

    ## Let next time pass
    

    ## Turn System
    users = [user_1]
    troves = [trove_1]

    system.take_turn(users, troves)
    assert system.time == SECONDS_PER_TURN

    system.take_turn(users, troves)
    system.take_turn(users, troves)
    system.take_turn(users, troves)
    system.take_turn(users, troves)
    system.take_turn(users, troves)
