import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from portfolio import Portfolio


def driver(p, cmd):
    split = cmd.split(' ')
    if split[0] == 'add': #add TICKER SHARES
        if split[1] == 'stocks': #add stocks TICKER SHARES TICKER SHARES
            for i in range(2,len(split)-1,2):
                print(p.add_stock(split[i],float(split[i+1])))
        else:
            print(p.add_stock(str(split[1]), float(split[2])))
    elif split[0] == 'rem' or split[0] == 'remove': #rem TICKER SHARES
        if split[1] == 'stocks': #rem stocks TICKER SHARES TICKER SHARES
            for i in range(2,len(split)-1,2):
                print(p.remove_stock(split[i],float(split[i+1])))
        if split[1] == 'all':
            for tick in p.tix:
                print(p.remove(tick))
        else:
            if len(split) < 3:
                print(p.remove_stock(str(split[1])))
            else:
                print(p.remove_stock(str(split[1]), float(split[2])))
    elif split[0] == 'print': #print
        if len(split) > 1:
            if split[1] == 'vol': #vol VOLATILITY
                p.generate_portfolio(int(split[2]))
            elif split[1] == 'optimal': #optimal
                p.print_opt()
            elif split[1] == 'gains': #gains
                p.print_gains()
            else:
                print('Command not recognized\n')
        else:
            p.print_portfolio()
    elif split[0] == 'plot': #plot
        if len(split) > 1:
            if split[1] == 'ef': #plot ef
                p.EF()
            elif split[1] == 'dist':
                if split[2] == 'stocks': #plot dist stocks
                    p.plot_logdist()
                elif split[2] == 'port' or split[2] == 'portfolio': #plot dist port
                    p.plot_portfolio_logdist()
                else:
                    print('Command not recognized\n')
            elif split[1] == 'mc':
                if len(split) == 2 or len(split == 3 and '-s' in split): p.monteCarlo(splitAssets=('-s' in split))
                elif len(split) == 3: p.monteCarlo(days=int(split[2]), splitAssets=('-s' in split))
                elif len(split) > 3: p.monteCarlo(days=int(split[2]), simulations=int(split[3]), splitAssets=('-s' in split))
            else:
                print('Command not recognized\n')
        else:
            p.plot_stocks()
    elif split[0] == 'saveas':
        p.saveas(str(split[1]))
    elif split[0] == 'save':
        p.save()
    elif split[0] == 'load':
        p = Portfolio(p.user.title())
        p.load(str(split[1]))
    elif split[0] == 'help':
        print('''
 Command (optional) [required]  | Explanation
________________________________|___________________________________________
 help                           | shows help menu
                                |
 load [filename]                | loads portfolio
                                | from [filename].csv
                                |
 save                           | saves portfolio 
                                | to [User].csv
                                |
 saveas [filename]              | saves portfolio 
                                | to [filename].csv
                                |                               
 add [stock] [shares]           | adds [shares] of [stock]
                                | to portfolio
                                |
 rem [stock] [shares]           | removes [shares] of [stock]
                                | to portfolio
                                |
 plot (ef)                      | plots price charts (efficient frontier)
                                |
 plot mc (days (n) (-s))        | plots Monte Carlo simulation for
                                | [days] and [n] simulations split 
                                | asset if [-s]
                                |
 plot dist (port/stocks)        | plots portfolio distribution/
                                | stock distributions
                                |
 print (vol [p]/optimal/gains)  | prints portfolio
                                | (portfolio on efficient
                                |  frontier with [p] 
                                |  percentile volatility/
                                |  optimal portfolio/
                                |  gains)
                                |
 exit                           | exits Finalyze
 
'''
            )
    else:
            print('\nCommand not recognized\n')
    return p

def main():
    print('''
Welcome to Finalyze!

For help enter 'help'

To load a portfolio from file, input '/' before user. (/user)

''')
    user = input('Portfolio user: ')
    if user[0] == '/':
        p = Portfolio(str(user[1:]).title())
        p.load(str(user[1:]).title())
    else:
        p = Portfolio(user.title())
    cmd = input('\nFinalyze Command>> ').lower()
    while cmd != 'exit':
        try:
            p = driver(p, cmd)
            cmd = input('\nFinalyze Command>> ').lower()
        except Exception as e:
            if user.lower() == 'debug': print(e)
            else:
                print('Something went wrong, please try again.')
                break
    print(f'\nThanks for using Finalyze, {p.user}!\n')

if __name__ == '__main__':
    main()