// Copyright © Aptos Foundation
// SPDX-License-Identifier: Apache-2.0

use crate::aggregator_extension::AggregatorID;

/// Returns a value of an aggregator from cache or global storage.
///   - Ok(..)       if aggregator value exists
///   - Err(..)      otherwise.
pub trait AggregatorResolver {
    fn resolve_aggregator_value(&self, id: &AggregatorID) -> Result<u128, anyhow::Error>;
}

// Utils to store aggregator values in data store. Here, we
// only care about aggregators which are state items.
#[cfg(any(test, feature = "testing"))]
pub mod test_utils {
    use super::*;
    use crate::{
        aggregator_extension::AggregatorHandle,
        delta_change_set::{deserialize, serialize},
    };
    use aptos_state_view::TStateView;
    use aptos_types::state_store::{
        state_key::StateKey, state_storage_usage::StateStorageUsage, state_value::StateValue,
        table::TableHandle,
    };
    use move_core_types::account_address::AccountAddress;
    use std::collections::HashMap;

    /// Generates a dummy id for aggregator based on the given key. Only used for testing.
    pub fn aggregator_id_for_test(key: u128) -> AggregatorID {
        let bytes: Vec<u8> = [key.to_le_bytes(), key.to_le_bytes()]
            .iter()
            .flat_map(|b| b.to_vec())
            .collect();
        let key = AggregatorHandle(AccountAddress::from_bytes(bytes).unwrap());
        AggregatorID::new(TableHandle(AccountAddress::ZERO), key)
    }

    #[derive(Default)]
    pub struct AggregatorStore(HashMap<StateKey, StateValue>);

    impl AggregatorStore {
        pub fn set_from_id(&mut self, id: AggregatorID, value: u128) {
            let AggregatorID { handle, key } = id;
            let state_key = StateKey::table_item(handle, key.0.to_vec());
            self.set_from_state_key(state_key, value);
        }

        pub fn set_from_state_key(&mut self, state_key: StateKey, value: u128) {
            self.0
                .insert(state_key, StateValue::new_legacy(serialize(&value)));
        }
    }

    impl AggregatorResolver for AggregatorStore {
        fn resolve_aggregator_value(&self, id: &AggregatorID) -> Result<u128, anyhow::Error> {
            let AggregatorID { handle, key } = id;
            let state_key = StateKey::table_item(*handle, key.0.to_vec());
            match self.get_state_value_bytes(&state_key)? {
                Some(bytes) => Ok(deserialize(&bytes)),
                None => {
                    anyhow::bail!("Could not find the value of the aggregator")
                },
            }
        }
    }

    impl TStateView for AggregatorStore {
        type Key = StateKey;

        fn get_state_value(&self, state_key: &Self::Key) -> anyhow::Result<Option<StateValue>> {
            Ok(self.0.get(state_key).cloned())
        }

        fn is_genesis(&self) -> bool {
            self.0.is_empty()
        }

        fn get_usage(&self) -> anyhow::Result<StateStorageUsage> {
            let mut usage = StateStorageUsage::new_untracked();
            for (k, v) in self.0.iter() {
                usage.add_item(k.size() + v.size())
            }
            Ok(usage)
        }
    }
}
