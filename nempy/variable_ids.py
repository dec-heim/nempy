import pandas as pd
from nempy import helper_functions as hf


def energy(capacity_bids, unit_info, next_variable_id):
    """Create decision variables that correspond to unit bids, for use in the linear program.

    This function defines the needed parameters for each variable, with a lower bound equal to zero, an upper bound
    equal to the bid volume, and a variable type of continuous. Bids that have a volume of zero are ignored and no
    variable is created. There is no limit on the number of bid bands and each column in the capacity_bids DataFrame
    other than unit is treated as a bid band. Volume bids should be positive numeric values only.

    Parameters
    ----------
    volume_bids : pd.DataFrame
        Bids by unit, in MW, can contain up to n bid bands.

        ========  ======================================================
        Columns:  Description:
        unit      unique identifier of a dispatch unit (as `str`)
        1         bid volume in the 1st band, in MW (as `float`)
        2         bid volume in the 2nd band, in MW (as `float`)
        n         bid volume in the nth band, in MW (as `float`)
        ========  ======================================================

    next_variable_id : int
        The next integer to start using for variables ids.

    Returns
    -------
    pd.DataFrame

        =============  ===============================================================
        Columns:       Description:
        unit           unique identifier of a dispatch unit (as `str`)
        capacity_band  the bid band of the variable (as `str`)
        variable_id    the id of the variable (as `int`)
        lower_bound    the lower bound of the variable, is zero for bids (as `float`)
        upper_bound    the upper bound of the variable, the volume bid (as `float`)
        type           the type of variable, is continuous for bids  (as `str`)
        =============  ===============================================================
    """

    bid_bands = [col for col in capacity_bids.columns if col != 'unit']
    stacked_bids = hf.stack_columns(capacity_bids, cols_to_keep=['unit'], cols_to_stack=bid_bands,
                                    type_name='capacity_band', value_name='upper_bound')

    stacked_bids = stacked_bids[stacked_bids['upper_bound'] > 0.0]
    stacked_bids = stacked_bids.sort_values(['unit', 'capacity_band'])
    stacked_bids = stacked_bids.reset_index(drop=True)
    stacked_bids = hf.save_index(stacked_bids, 'variable_id', next_variable_id)
    stacked_bids['lower_bound'] = 0.0
    stacked_bids['type'] = 'continuous'
    stacked_bids['service'] = 'energy'
    stacked_bids['coefficient'] = 1.0
    stacked_bids = pd.merge(stacked_bids, unit_info.loc[:, ['unit', 'region']], 'inner', on='unit')
    return stacked_bids.loc[:, ['variable_id', 'unit', 'capacity_band', 'lower_bound', 'upper_bound', 'type', 'region',
                                'service', 'coefficient']]
