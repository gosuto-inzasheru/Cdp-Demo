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

MAX_BPS = 10_000



INTERNAL_SECONDS_SINCE_DEPLOY = 0

MAX_LTV = 15000 ## 150%
FEE_PER_SECOND = 0 ## No fee for borrows
ORIGINATION_FEE = 50 ## 50BPS


INITIAL_FEED = 1000


def IS_IN_EMERGENCY_MODE():
  ## TODO:
  return False



class Global():
  def __init__(self):
    self.total_deposits = 0
    self.total_debt = 0
    self.time_since_deploy = 0
    self.feed = INITIAL_FEED
  
  ## SETTERS ##
  
  def UPDATE_DEBT(self, amount):
    self.total_debt += amount

  def UPDATE_DEPOSITS(self, amount):
    self.total_deposits += amount

  def GLOBAL_COLLATERAL_RATIO(self):
    return self.total_debt * MAX_BPS / self.total_deposits 
  
  def GLOBAL_MAX_BORROW(self):
    return self.total_deposits * self.feed
  
  def IS_IN_EMERGENCY_MODE(self):
    return False
  
  def IS_SOLVENT(self):
    return self.total_debt < self.GLOBAL_MAX_BORROW()

  def get_feed(self):
    return self.feed
    
  ## SUPER POWERS ##
  def time_travel(self, amount):
    self.time_since_deploy += amount
  
  def set_feed(self, price):
    self.feed = price
  



class Trove():
  def __init__(self, world, owner):
    self.deposits = 0
    self.debt = 0
    self.last_update_ts = INTERNAL_SECONDS_SINCE_DEPLOY
    self.owner = owner
    self.world = world
  
  def local_collateral_ratio(self):
    return self.debt * MAX_BPS / self.deposits
  
  def deposit(self, amount):
    self.deposits += amount
    self.world.UPDATE_DEPOSITS(amount)

    self.owner.reduce_balance(self, amount)
  
  def withdraw(self, amount):
    self.deposits -= amount
    self.world.UPDATE_DEPOSITS(-amount)

    assert self.is_solvent()
  
  def borrow(self, amount):
    self.debt += amount
    self.world.UPDATE_DEBT(amount)

    assert self.is_solvent()
  
  def repay(self, amount):
    self.debt -= amount
    self.world.UPDATE_DEBT(-amount)

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
    return self.deposits * self.world.get_feed()
  
  def is_solvent(self):
    ## Strictly less to avoid rounding or w/e
    return self.debt < self.max_borrow() 
  

  

class User():
  def __init__(self, initial_balance_collateral, name):
    self.collateral = initial_balance_collateral
    self.name = name ## TODO: Random Name Generator
  
  def increase_balance(self, caller, amount):
    try:
      assert caller.is_trove() == True
      self.collateral += amount

    except:
        ## Do nothing on failure
        print("increase_balance error")
    
  def reduce_balance(self, caller, amount):
    try:
      assert caller.is_trove() == True
      self.collateral -= amount

    except:
        ## Do nothing on failure
        print("reduce_balance error")
  
  def get_balance(self):
    return self.collateral


## POOL For Swap

class UniV2Pool():
  def __init__(self, start_x, start_y):
    ## NOTE: May or may not want to have a function to hardcode this
    self.reserve_x = start_x
    self.reserve_y = start_y

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

  draw_down_smooth_sim(0)



def draw_down_smooth_sim(drawdown_value):
  world = Global()

  ## 1 eth
  first_user = User(1e18, "A")

  ## One trove so this sim is just a more detailed copy of `drawdown_sim`
  global_trove = Trove(world, first_user)

  assert global_trove.max_borrow() == 0

  global_trove.deposit(1e18)
  max_borrow = global_trove.max_borrow()

  assert max_borrow > 0

  assert world.IS_SOLVENT()

  ## Test to see if insolvency is detected
  world.set_feed(0)

  assert not world.IS_SOLVENT()