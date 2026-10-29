pipeline {
    agent { label 'built-in' }
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        quietPeriod(15)
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }
    triggers { githubPush() }
    stages {
        stage('Checkout main') {
            steps {
                script {
                    def revision = checkout scm
                    if (!(revision.GIT_COMMIT ==~ /[a-f0-9]{40}/)) {
                        error('Invalid Git commit returned by SCM')
                    }
                    env.HALLT_COMMIT = revision.GIT_COMMIT
                }
                sh 'command -v git >/dev/null && command -v ssh >/dev/null'
            }
        }
        stage('Validate and deploy') {
            steps {
                withCredentials([
                    sshUserPrivateKey(credentialsId: 'hallt-deploy-ssh', keyFileVariable: 'HALLT_KEY'),
                    file(credentialsId: 'hallt-known-hosts', variable: 'HALLT_HOST_KEYS'),
                    string(credentialsId: 'hallt-deploy-target', variable: 'HALLT_TARGET')
                ]) {
                    sh '''#!/bin/sh
set -eu
ssh -i "$HALLT_KEY" \
    -o BatchMode=yes \
    -o IdentitiesOnly=yes \
    -o StrictHostKeyChecking=yes \
    -o UserKnownHostsFile="$HALLT_HOST_KEYS" \
    -o ConnectTimeout=10 \
    -o ServerAliveInterval=15 \
    -o ServerAliveCountMax=3 \
    -- "$HALLT_TARGET" "$HALLT_COMMIT"
'''
                }
            }
        }
    }
    post {
        success { echo 'Hallt origin HTTPS verified, or superseded revision safely skipped. See deployment output.' }
        failure { echo 'Deployment failed. The host attempts rollback if publication had started; inspect its result in this build log.' }
    }
}
