script {
    use aptos_framework::aptos_coin;
    use aptos_framework::coin;

    use std::signer;

    /// An example of a **test-and-abort** attack that fails thanks to `decide_winners`
    /// being marked as *private* entry function.
    fun main(attacker: &signer) {
        let attacker_addr = signer::address_of(attacker);

        let old_balance = coin::balance<aptos_coin::AptosCoin>(attacker_addr);

        // SECURITY: The fact that `decide_winners` is a *private* entry function is what
        // prevents this call here. The compiler will output the following error:
        //
        // ```
        //    error[E04001]: restricted visibility
        //    |- /tmp/aptos-core/aptos-move/move-examples/lottery/scripts/test_and_abort_attack_defeated.move:19:9
        //    |
        //    19 |         lottery::lottery::decide_winners();
        //    |         ^^^^^^^^^^^^^^^^^^^^^^^^^ Invalid call to '(lottery=0xC3BB8488AB1A5815A9D543D7E41B0E0DF46A7396F89B22821F07A4362F75DDC5)::lottery::decide_winners'
        //    |
        //    |- /tmp/aptos-core/aptos-move/move-examples/lottery/sources/lottery.move:122:15
        //    |
        //    122 |     entry fun decide_winners() acquires Lottery, Credentials {
        //    |               -------------- This function is internal to its module. Only 'public' and 'public(friend)' functions can be called outside of their module
        // ```

        // TODO: Uncomment this call to reproduce the error above & see the attack failing.
        // (Commented out to ensure this Move example compiles.)
        //lottery::lottery::decide_winners();

        let new_balance = coin::balance<aptos_coin::AptosCoin>(attacker_addr);

        // The attacker can see if his balance remained the same. If it did, then
        // the attacker knows they did NOT win the lottery and can abort everything.
        if (new_balance == old_balance) {
            abort(1)
        };
    }
}
