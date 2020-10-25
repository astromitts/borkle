from django import template

register = template.Library()


@register.filter
def pdb(item1, item2=None):
    import pdb
    pdb.set_trace()


@register.filter
def get(item1, item2=None):
    return item1.get(item2)


@register.filter
def get_dice_image(dice_value):
    return 'images/dice/{}.png'.format(dice_value)

@register.filter
def get_dice_images(selection):
    dice_imgs = []
    selection_vals = selection.scored_values
    if selection_vals['score'] == 0:
        dice_imgs.append('images/dice/0.png')
    else:
        for die, data in selection_vals['dice'].items():
            dice_imgs.append('images/dice/{}.png'.format(data['value']))
    return dice_imgs
