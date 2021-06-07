from vaccine_efficacy_article.build_input_files.refdat_age_pyr import find_age_pyramid
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Patch
import matplotlib as mpl
import os

mpl.rcParams['pdf.fonttype'] = 42
rcParams.update({'font.size': 16})

fig_dir = './figures'
os.makedirs(fig_dir, exist_ok=True)


countries = ['Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Central African Republic',
                 'Chad', 'Ivory Coast', 'DRC', 'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea',
                 'Guinea-Bissau', 'Kenya', 'Lesotho', 'Liberia', 'Madagascar', 'Malawi', 'Mali', 'Mauritania',
                 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Senegal', 'Sierra Leone',
                 'South Africa', 'Tanzania', 'Togo', 'Uganda', 'Zambia', 'Zimbabwe']

age_pyr_x, age_pyr_y_rural = find_age_pyramid(arg_key='AFRO:REP', countries=countries, area='Rural')
age_pyr_x, age_pyr_y_urban = find_age_pyramid(arg_key='AFRO:REP', countries=countries, area='Urban')

age_pyr_y_rural = [z*100 for z in age_pyr_y_rural]
age_pyr_y_urban = [z*100 for z in age_pyr_y_urban]

plt.rcdefaults()
fig, ax = plt.subplots()

# Example data

ax.barh(range(0, 16), age_pyr_y_urban[::-1], align='center', color='xkcd:blue')
ax.barh(range(0, 16), age_pyr_y_rural[::-1], align='center', alpha=0.7, color='xkcd:orange')
ax.set_yticks(range(1, 16, 2))
ax.set_yticklabels(['%sy - %sy' % (a, a+5) for a in age_pyr_x[0:16:2][::-1]], fontsize=12)
ax.set_xticks([0.0, 5, 10, 15, 20])
ax.set_xticklabels(['0%', '5%', '10%', '15%', '20%'], fontsize=12)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Percent of population', fontsize=12)

custom_lines_2 = [Patch(color=c, alpha=1-i*0.3) for i, c in enumerate(['xkcd:blue', 'xkcd:orange'])]
fig.legend(custom_lines_2, ['Urban', 'Rural'],
           bbox_to_anchor=(0.95, 0.97), ncol=1, fontsize=12)
plt.savefig(os.path.join(fig_dir, 'Age_pyramid.png'))
plt.savefig(os.path.join(fig_dir, 'Age_pyramid.pdf'))
plt.show()