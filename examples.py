class SigmaAdMan(admin.ModelAdmin):
exclude = ('category',)

def save_model(self, request, obj, form, change):
    obj.category = 2
    obj.save()







def game(x, y, move='start', spacer=''):
    ''' returns win/lose in boolean '''
    print(move)
    if 1<=x<=15 and 1<=y<=15:
        print(x, y)
        # test1
        move1 = game(x-2, y+1, 'move1', spacer=spacer+' ')
        move2 = game(x-2, y-1,'move2', spacer=spacer+' ')
        move3 = game(x+1, y-2,'move3', spacer=spacer+' ')
        move4 = game(x-1, y-2,'move4', spacer=spacer+' ')
        print(spacer + str(not move1) + ' ' + str(not move2) + ' ' + str(not move3) + ' ' + str(not move4))
        return not move1 or not move2 or not move3 or not move4
    else:
        print(spacer + move + ' deadEndTrue')
        return True






# initial start
3,2

# move1
